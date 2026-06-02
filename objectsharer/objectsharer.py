# ObjectSharer v2 with ZMQ communication backend
# Reinier Heeres <reinier@heeres.eu>, 2013
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
ObjectSharer: peer-to-peer remote Python objects over ZeroMQ.

Architecture
------------
Each process runs an ObjectSharer instance (global ``helper``) backed by a
``ZMQBackend``. The backend listens on a ROUTER socket and maintains one DEALER
socket per remote peer. Communication is bidirectional once connected; there is
no strict client/server hierarchy beyond who initiates the first ``hello_from``.

Main components:
  - ``ObjectSharer`` (``helper``): registry, RPC dispatch, signals, proxies
  - ``ZMQBackend``: sockets, event loop, connection handshake
  - ``ObjectProxy`` / ``_FunctionCall``: client-side remote object stand-ins
  - ``root`` (``RootObject``): well-known object every peer registers as ``root``

Wire protocol (pickled tuple, first element is message type)
-------------------------------------------------------------
  - ``OS_CALL`` ('c'): remote method invocation; may carry ``OS_SIG`` in kwargs
  - ``OS_RETURN`` ('r'): RPC reply keyed by call id
  - ``hello_from``: connection handshake with peer address
  - ``goodbye_from``: tear down connection state
  - ``ping`` / ``pong``: liveness check

Serialization markers embedded in call/return payloads:
  - ``OS_AR``: numpy array sent as separate binary frame (zero-copy)
  - ``OS_UID`` / ``OS_SRV_ID`` / ``OS_SRV_ADDR``: shared object reference

Threading
---------
ZMQ sockets are not thread-safe. All ObjectSharer I/O must run in the thread
that owns the backend's main loop (or via ``add_qt_timer`` for Qt integration).
"""

import bisect
import inspect
import logging
import os
import pickle
import random
import time
import traceback
import uuid

import numpy as np
import zmq

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logger = logging.getLogger("Object Sharer")
logger.setLevel(logging.INFO)
_handler = logging.StreamHandler()
_handler.setLevel(logging.WARNING)
_handler.setFormatter(logging.Formatter('%(name)s:%(levelname)s:%(message)s'))
logger.addHandler(_handler)

# ---------------------------------------------------------------------------
# Constants and protocol tags
# ---------------------------------------------------------------------------

DEFAULT_TIMEOUT = 600000  # RPC timeout in milliseconds

# Legacy scheduling hack: repeated os.getcwd() after send may reduce latency.
REDUCE_LATENCY = True

OS_CALL = 'c'
OS_RETURN = 'r'
OS_SIGNAL = 'OS_SIG'

# Dunder methods forwarded from ObjectProxy to remote callables.
SPECIAL_FUNCTIONS = (
    '__getitem__',
    '__setitem__',
    '__delitem__',
    '__contains__',
    '__str__',
    '__repr__',
)

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class RemoteException(Exception):
    """Exception raised on the remote side and re-raised on the caller."""


class TimeoutError(RuntimeError):
    """Raised when a synchronous RPC or connection handshake times out."""


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def ellipsize(s):
    """Truncate long strings for debug log lines."""
    if len(s) > 64:
        return s[:64] + '...'
    return s


def _argspec_to_parts(args, defaults, varargs, varkw, kwonlyargs=None, kwonlydefaults=None):
    """Build a parenthesized argument list string from inspect argspec fields."""
    args = list(args or [])
    if args and args[0] in ('self', 'cls'):
        args = args[1:]
    parts = []
    defaults = defaults or ()
    offset = len(args) - len(defaults)
    for i, name in enumerate(args):
        if i >= offset:
            parts.append(f'{name}={defaults[i - offset]!r}')
        else:
            parts.append(name)
    if varargs:
        parts.append(f'*{varargs}')
    kwonly = kwonlyargs or ()
    if kwonly:
        if not varargs:
            parts.append('*')
        kwdefaults = kwonlydefaults or {}
        for name in kwonly:
            if name in kwdefaults:
                parts.append(f'{name}={kwdefaults[name]!r}')
            else:
                parts.append(name)
    if varkw:
        parts.append(f'**{varkw}')
    return f"({', '.join(parts)})"


def _format_argspec_for_doc(argspec):
    """Format stored signature metadata for proxy function docstrings."""
    if argspec is None:
        return '()'
    if isinstance(argspec, str):
        return argspec if argspec.startswith('(') else f'({argspec})'

    if isinstance(argspec, inspect.FullArgSpec):
        return _argspec_to_parts(
            argspec.args, argspec.defaults, argspec.varargs, argspec.varkw,
            argspec.kwonlyargs, argspec.kwonlydefaults,
        )

    # Legacy Argspec named tuple from inspect.getargspec() (Python 2 peers).
    if hasattr(argspec, 'args') and hasattr(argspec, 'keywords') and not hasattr(argspec, 'kwonlyargs'):
        return _argspec_to_parts(
            argspec.args, argspec.defaults, argspec.varargs, argspec.keywords,
        )

    return '()'


def cache_result(f):
    """Decorator: cache the return value on the client-side proxy."""
    if not hasattr(f, '_share_options'):
        f._share_options = {}
    f._share_options['cache_result'] = True
    return f


# ---------------------------------------------------------------------------
# Serialization: wrap / unwrap numpy arrays and shared object references
# ---------------------------------------------------------------------------

def _walk_objects(obj, func, *args):
    """Recursively apply *func* to *obj* and nested list/tuple/dict contents."""
    if type(obj) in (list, tuple):
        # Copy containers so we can rewrite nested values without mutating the
        # original tuple/list object that may still be referenced by callers.
        obj = list(obj)
        for i, v in enumerate(obj):
            obj[i] = _walk_objects(v, func, *args)
    if type(obj) is dict:
        # Sort keys for deterministic traversal; this keeps serialization and
        # debugging output stable across Python versions.
        for k in sorted(obj):
            obj[k] = _walk_objects(obj[k], func, *args)
    return func(obj, *args)


def _wrap_ars_sobjs(obj, arlist=None):
    """Replace numpy arrays and shared objects with wire-serializable markers."""
    def replace(o):
        if isinstance(o, np.ndarray):
            # Send array metadata in the pickle payload and the raw bytes in a
            # separate ZeroMQ frame so large arrays do not get copied twice.
            if not o.flags['C_CONTIGUOUS']:
                o = np.ascontiguousarray(o)
            assert o.flags['C_CONTIGUOUS']
            arlist.append(o)
            return dict(OS_AR=True, shape=o.shape, dtype=o.dtype)
        if hasattr(o, '_OS_UID'):
            # Shared objects become lightweight references. The receiver can
            # turn these back into proxies if it knows the owner uid/address.
            ret = dict(OS_UID=o._OS_UID)
            if hasattr(o, '_OS_SRV_ID'):
                ret['OS_SRV_ID'] = o._OS_SRV_ID
                ret['OS_SRV_ADDR'] = o._OS_SRV_ADDR
            return ret
        return o

    if arlist is None:
        arlist = []
    try:
        obj = _walk_objects(obj, replace)
        return obj, arlist
    except Exception:
        return obj, arlist


def _unwrap_ars_sobjs(obj, bufs, client=None):
    """Restore numpy arrays and shared object proxies from wire markers."""
    def replace(o):
        if type(o) is dict:
            if 'OS_AR' in o:
                # Rebuild arrays from the next raw frame in the multipart message.
                if len(bufs) == 0:
                    raise ValueError('No buffer!')
                ar = np.frombuffer(bufs.pop(0), dtype=o['dtype'])
                return ar.reshape(o['shape'])
            if 'OS_UID' in o:
                # Prefer the explicit server address if it came back in the
                # payload; otherwise resolve via the client that sent the frame.
                if 'OS_SRV_ID' in o and 'OS_SRV_ADDR' in o:
                    return helper.get_object_from(o['OS_UID'], o['OS_SRV_ID'], o['OS_SRV_ADDR'])
                return helper.get_object_from(o['OS_UID'], client)
        return o

    obj = _walk_objects(obj, replace)
    return obj, bufs


# ---------------------------------------------------------------------------
# Asynchronous reply helpers
# ---------------------------------------------------------------------------

class AsyncReply(object):
    """
    Holds the result of an asynchronous RPC.

    Poll ``is_valid()`` or call ``get(block=True)`` to wait for the reply.
    """

    def __init__(self, callid, callback=None):
        self._callid = callid
        self.val_valid = False
        self.val = None
        self.callback = callback

    def set(self, val):
        self.val = val
        self.val_valid = True
        if self.callback is not None:
            logger.debug(f'Performing callback for call id {int(self._callid)}', )
            self.callback(val)

    def get(self, block=False, delay=DEFAULT_TIMEOUT, do_raise=True):
        if block and not self.is_valid():
            helper.interact(delay=delay)
        if do_raise and isinstance(self.val, Exception):
            raise self.val
        return self.val

    def is_valid(self):
        return self.val_valid


class AsyncHelloReply(object):
    """Waits until a peer address is mapped to a ZMQ identity (uid)."""

    def __init__(self, target):
        self.target = target
        self.val = None

    def is_valid(self):
        self.val = helper.backend.get_uid_for_addr(self.target)
        return self.val is not None


# ---------------------------------------------------------------------------
# ObjectSharer core
# ---------------------------------------------------------------------------

class ObjectSharer(object):
    """
    Central registry and RPC dispatcher for shared Python objects.

    Attach a ``ZMQBackend`` via ``set_backend()`` before making remote calls.
    Lab scripts typically use the module-level ``helper`` singleton instead of
    constructing their own instance.
    """

    def __init__(self):
        self.backend = None

        # Locally registered objects keyed by uid; name_map holds alias -> uid.
        self.objects = {}
        self.name_map = {}

        # Remote peers and cached proxies. `_proxy_cache` avoids rebuilding the
        # same ObjectProxy repeatedly, and `_client_object_list_cache` lets us
        # resolve names without querying every peer.
        self.clients = {}
        self._proxy_cache = {}
        self._client_object_list_cache = {}

        self._last_call_id = 0
        self.reply_objects = {}

        # Signal (pub/sub-style callback) state.
        self._last_hid = 0
        self._callbacks_hid = {}
        self._callbacks_name = {}
        self._signal_queue = []
        self.announced_clients = set()

    def set_backend(self, backend):
        self.backend = backend

    def interact(self, delay=DEFAULT_TIMEOUT, wait_for=None):
        """Process incoming messages until timeout or *wait_for* completes."""
        self.backend.main_loop(delay=delay, wait_for=wait_for, origin=1)

    def call(self, client, obj_name, func_name, *args, **kwargs):
        """Invoke a method on a remote object (sync or async)."""
        is_signal = kwargs.get(OS_SIGNAL, False)
        callback = kwargs.pop('callback', None)
        async_ = kwargs.pop('async_', False) or (callback is not None) or is_signal
        timeout = kwargs.pop('timeout', DEFAULT_TIMEOUT)

        self._last_call_id += 1
        callid = self._last_call_id
        async_reply = AsyncReply(callid, callback=callback)
        self.reply_objects[callid] = async_reply
        logger.debug(
            f'Sending call {int(callid)} to {client}: {obj_name}.{func_name}({ellipsize(str(args))},{ellipsize(str(kwargs))}), async={async_}',
            )

        # Wrap arrays/shared objects before pickling so the main message stays
        # small and the heavy binary payload can ride in separate frames.
        args, arlist = _wrap_ars_sobjs(args)
        kwargs, arlist = _wrap_ars_sobjs(kwargs, arlist)
        msg = (OS_CALL, callid, obj_name, func_name, args, kwargs)
        try:
            msg = pickle.dumps(msg)
        except Exception:
            raise Exception(f'Unable to pickle function call: {str(msg)}')
        self.backend.send_to(client, msg, arlist)

        if async_:
            return async_reply

        ret = self.backend.main_loop(delay=timeout, wait_for=async_reply, origin=2)
        if ret:
            return async_reply.get()
        raise TimeoutError('Call timed out')

    # ----- Object registry and lookup -----

    def list_objects(self):
        """Return uids and aliases of all locally registered objects."""
        ret = list(self.objects.keys())
        ret.extend(list(self.name_map.keys()))
        return ret

    def get_object(self, objname):
        """Return a local object by uid or alias."""
        objname = self.name_map.get(objname, objname)
        return self.objects.get(objname, None)

    def _get_object_shared_props_funcs(self, obj):
        """Introspect *obj* to build the metadata dict sent to remote proxies."""
        props = []
        funcs = []
        for key, val in inspect.getmembers(obj):
            # Keep the proxy surface focused: hide private members, but preserve
            # a few dunder methods that are meant to be invoked remotely.
            if key.startswith('_') and key not in SPECIAL_FUNCTIONS:
                continue
            # 'connect' is reserved locally for signal wiring on proxies.
            if key == 'connect':
                continue
            if callable(val):
                # Capture docs and signatures so remote proxies can synthesize
                # useful method wrappers and introspection strings.
                opts = val._share_options if hasattr(val, '_share_options') else {}
                opts = dict(opts)
                opts['__doc__'] = getattr(val, '__doc__', None)
                try:
                    opts['__argspec__'] = str(inspect.signature(val))
                except (ValueError, TypeError):
                    opts['__argspec__'] = None
                funcs.append((key, opts))
            else:
                props.append(key)
        return props, funcs

    def get_object_info(self, objname):
        """Return introspection metadata for building a remote ``ObjectProxy``."""
        obj = self.get_object(objname)
        if obj is None:
            return None
        props, funcs = self._get_object_shared_props_funcs(obj)
        return dict(uid=obj._OS_UID, properties=props, functions=funcs)

    def get_object_info_from(self, objname, client_id, client_addr=None):
        """Fetch object metadata from a remote peer, connecting if needed."""
        if client_id not in self.clients:
            if client_addr is None:
                logger.warning('Object from unknown client requested')
                return None
            logger.info(
                f'Object {objname} requested from unconnected client {client_id} @ {client_addr}, connecting...',
                )
            self.backend.connect_to(client_addr, uid=client_id)

        if client_id not in self.clients:
            logger.error('Unable to connect to client')
            return None

        try:
            return self.clients[client_id].get_object_info(objname)
        except TimeoutError:
            logger.warning(f'Client {client_id} unresponsive: Removing from connected', )
            del self.clients[client_id]
            return None

    def get_object_from(self, objname, client_id, client_addr=None, no_cache=False):
        """Return an ``ObjectProxy`` for a remote object, using cache when possible."""
        if not no_cache:
            cached = self._proxy_cache.get(objname)
            if cached is not None and cached._OS_SRV_ID == client_id:
                return cached

        info = self.get_object_info_from(objname, client_id, client_addr=client_addr)
        if info is None:
            return None
        proxy = ObjectProxy(client_id, info)
        self._proxy_cache[objname] = proxy
        self._proxy_cache[proxy.os_get_uid()] = proxy
        return proxy

    def find_object(self, objname, client_id=None, client_addr=None, no_cache=False):
        """Resolve *objname* locally, from cache, or by querying connected peers."""
        if client_id is not None:
            return self.get_object_from(objname, client_id, client_addr)

        obj = self.get_object(objname)
        if obj is not None:
            return obj

        if not no_cache:
            if objname in self._proxy_cache:
                return self._proxy_cache[objname]
            for cid, names in self._client_object_list_cache.items():
                if objname in names:
                    return self.get_object_from(objname, cid)

        for cid in list(self.clients.keys()):
            obj = self.get_object_from(objname, cid, no_cache=no_cache)
            if obj is not None:
                return obj
        return None

    def register(self, obj, name=None):
        """
        Register *obj* for remote access.

        Assigns ``obj._OS_UID``, optional alias in ``name_map``, and wires
        ``obj.emit`` / ``obj.connect`` for the signal system.
        """
        if obj is None:
            return
        if hasattr(obj, '_OS_UID') and obj._OS_UID is not None:
            logger.warning(f'Object {obj._OS_UID} already registered', )
            return

        obj._OS_UID = str(uuid.uuid4())
        if name is not None:
            if name in self.name_map:
                raise Exception(f'Object {name} already defined')
            self.name_map[name] = obj._OS_UID

        # Monkey-patch the object so its signal API transparently routes through
        # ObjectSharer. Existing emit/connect callers do not need to know about
        # the networking layer.
        obj._OS_emit = getattr(obj, 'emit', None)
        obj.emit = lambda signal, *a, **kw: self.emit_signal(obj._OS_UID, signal, *a, **kw)
        obj.connect = lambda signame, callback, *a, **kw: self.connect_signal(
            obj._OS_UID, signame, callback, *a, **kw,
        )
        self.objects[obj._OS_UID] = obj
        root.emit('object-added', obj._OS_UID, name=name)

    def add_client(self, name):
        """Record a client name announced via ``RootObject.client_announce``."""
        self.announced_clients.add(name)

    def unregister(self, obj):
        if not hasattr(obj, '_OS_UID'):
            logger.warning('Trying to unregister an unknown object')
            return

        if obj._OS_UID in self.objects:
            del self.objects[obj._OS_UID]
            root.emit('object-removed', obj._OS_UID)

        for alias, uid in list(self.name_map.items()):
            if obj._OS_UID == uid:
                del self.name_map[alias]

    # ----- Signals -----

    def connect_signal(self, uid, signame, callback, *args, **kwargs):
        """Register a local callback for ``signame`` on object *uid*."""
        self._last_hid += 1
        info = {
            'hid': self._last_hid,
            'uid': uid,
            'signal': signame,
            'callback': callback,
            'args': args,
            'kwargs': kwargs,
        }
        self._callbacks_hid[self._last_hid] = info
        name = f'{uid}__{signame}'
        self._callbacks_name.setdefault(name, []).append(info)
        return self._last_hid

    def disconnect_signal(self, hid):
        if hid in self._callbacks_hid:
            del self._callbacks_hid[hid]
        for name, info_list in self._callbacks_name.items():
            for index, info in enumerate(info_list):
                if info['hid'] == hid:
                    del self._callbacks_name[name][index]
                    break

    def emit_signal(self, uid, signame, *args, **kwargs):
        """Broadcast a signal to all connected peers and local callbacks."""
        logger.debug(
            f'Emitting {signame}({args!r}, {kwargs!r}) for {uid} to {len(self.clients)} clients',
            )
        # Signals are just RPC calls with a special marker; remote peers and
        # local callbacks both see the same event payload.
        kwargs[OS_SIGNAL] = True
        for client in self.clients.values():
            client.receive_signal(uid, signame, *args, **kwargs)
        self.receive_signal(uid, signame, *args, **kwargs)

    def receive_signal(self, uid, signame, *args, **kwargs):
        kwargs.pop(OS_SIGNAL, None)
        logger.debug(f'Received signal {signame}({args!r}, {kwargs!r}) from {uid}', )

        ncalls = 0
        start = time.time()
        name = f'{uid}__{signame}'
        # Each callback can add its own positional/keyword extras that are
        # appended here before invocation.
        for info in self._callbacks_name.get(name, []):
            ncalls += 1
            try:
                fargs = list(args)
                fargs.extend(info['args'])
                fkwargs = kwargs.copy()
                fkwargs.update(info['kwargs'])
                info['callback'](*fargs, **fkwargs)
            except Exception as e:
                logger.warning(
                    f"Callback to {info.get('callback', None)} failed for {uid}.{signame}: {e!s}\n{traceback.format_exc()}",
                    )

        elapsed_ms = (time.time() - start) * 1000
        logger.debug(f'Did {int(ncalls)} callbacks in {elapsed_ms:.03f}ms for sig {signame}', )

    # ----- Client management -----

    def _update_client_object_list(self, uid, names):
        if names is not None:
            self._client_object_list_cache[uid] = names

    def _add_client_to_list(self, uid, root_info):
        if root_info is None:
            raise Exception(f'Unable to retrieve root object from {uid}')
        logger.debug(f'  root@{uid}.get_object_info() reply: {root_info}', )
        self.clients[uid] = ObjectProxy(uid, root_info)
        self.clients[uid].list_objects(
            callback=lambda reply, uid=uid: self._update_client_object_list(uid, reply),
        )

    def request_client_proxy(self, uid, async_=False):
        """Fetch the remote ``root`` object and register the peer in ``clients``."""
        # Every peer publishes a well-known `root` object. We fetch that first,
        # then ask root for its object list so the proxy cache can be populated.
        if not async_:
            info = self.call(uid, 'root', 'get_object_info', 'root')
            self._add_client_to_list(uid, info)
        else:
            self.call(
                uid, 'root', 'get_object_info', 'root',
                callback=lambda reply, uid=uid: self._add_client_to_list(uid, reply),
            )

    # ----- Incoming message dispatch -----

    def process_message(self, from_uid, info, bufs, waiting=False):
        """
        Dispatch one decoded wire message.

        When *waiting* is True (main loop blocked on an RPC reply), incoming
        signals are queued rather than handled inline to avoid re-entrancy.
        """
        # The first tuple entry is the message type; everything else is routed
        # to a specialized handler.
        msg_type = info[0]
        if msg_type == OS_CALL:
            self._handle_call(from_uid, info, bufs, waiting)
        elif msg_type == OS_RETURN:
            self._handle_return(from_uid, info, bufs)
        elif msg_type == 'hello_from':
            self._handle_hello(from_uid, info)
        elif msg_type == 'goodbye_from':
            self._handle_goodbye(from_uid, info)
        elif msg_type == 'ping':
            self._handle_ping(from_uid)
        elif msg_type == 'pong':
            logger.debug('PONG')
        else:
            logger.debug(f'Unknown msg: {info}', )

    def _handle_call(self, from_uid, info, bufs, waiting):
        obj = None
        func = None
        objid = funcname = None
        callid = info[1] if len(info) > 1 else None
        try:
            callid, objid, funcname, args, kwargs = info[1:6]
            sig = kwargs.get(OS_SIGNAL, False)

            # Defer signal delivery while a synchronous RPC is in flight.
            if waiting and sig:
                # This keeps signal callbacks from re-entering the call stack
                # while we are blocked waiting for a reply message.
                self._signal_queue.append((from_uid, info, bufs))
                return

            # Rehydrate arrays/shared objects before invoking the real method.
            args, bufs = _unwrap_ars_sobjs(args, bufs, from_uid)
            kwargs, bufs = _unwrap_ars_sobjs(kwargs, bufs, from_uid)

            logger.debug(f'  Processing call {callid}: {objid}.{funcname}({args},{kwargs})', )

            obj = self.get_object(objid)
            func = getattr(obj, funcname, None)
            ret = func(*args, **kwargs)

            if sig:
                return

            ret, bufs = _wrap_ars_sobjs(ret)
            logger.debug(f'  Returning for call {callid}: {ellipsize(str(ret))}', )

        except Exception as e:
            if len(info) < 6:
                logger.error(f'Invalid call msg: {info}', )
                ret = RemoteException('Invalid call msg')
            elif obj is None:
                ret = RemoteException(f'Object {objid} not available')
            elif func is None:
                ret = RemoteException(f'Object {objid} does not have function {funcname}')
            else:
                ret = RemoteException(f'{e}\n{traceback.format_exc(15)}')

        try:
            msg = pickle.dumps((OS_RETURN, callid, ret))
        except Exception:
            ret = RemoteException(f'Unable to pickle return {str(ret)}')
            msg = pickle.dumps((OS_RETURN, callid, ret))
            bufs = None
        self.backend.send_to(from_uid, msg, bufs)

    def _handle_return(self, from_uid, info, bufs):
        if len(info) < 3:
            logger.error(f'Invalid return msg: {info}', )
            return

        callid, ret = info[1:3]
        ret, bufs = _unwrap_ars_sobjs(ret, bufs, from_uid)

        if callid in self.reply_objects:
            self.reply_objects[callid].set(ret)
            del self.reply_objects[callid]
        else:
            raise Exception(f'Reply for unknown call {callid}')

    def _handle_hello(self, from_uid, info):
        """
        Complete bidirectional handshake: map peer address to uid and open
        reverse DEALER connection if we are not already connected.
        """
        logger.debug(f'Client {from_uid} connected from {info[1]}', )
        self.backend.connect_from(info[1], from_uid)
        if not self.backend.connected_to(from_uid):
            logger.debug('Initiating reverse connection...')
            self.backend.connect_to(info[1])
            self.request_client_proxy(from_uid, async_=True)

    def _handle_goodbye(self, from_uid, info):
        logger.debug(f'Goodbye client {from_uid} from {info[1]}', )
        forget_uid = self.backend.get_uid_for_addr(info[1])
        if forget_uid in self.clients:
            del self.clients[forget_uid]
            logger.debug(f'deleting client {forget_uid}', )
        self.backend.forget_connection(info[1], remote=False)
        if from_uid in self.clients:
            del self.clients[from_uid]
            logger.debug(f'deleting client {from_uid}', )

    def _handle_ping(self, from_uid):
        logger.debug('PING')
        self.backend.send_to(from_uid, pickle.dumps(('pong',)))

    def flush_queue(self, nmax=5):
        """Process up to *nmax* deferred signals. Returns True if queue is empty."""
        for _ in range(nmax):
            if not self._signal_queue:
                break
            from_uid, info, bufs = self._signal_queue.pop(0)
            self.process_message(from_uid, info, bufs)
        return len(self._signal_queue) == 0


# ---------------------------------------------------------------------------
# Root object, proxy call wrapper, and client-side proxy
# ---------------------------------------------------------------------------

class RootObject(object):
    """
    Well-known object registered as ``root`` on every ObjectSharer instance.

    Remote peers use it to list objects and fetch introspection metadata.
    """

    def hello_world(self):
        return 'Hello world!'

    def hello_exception(self):
        return 1 / 0

    def client_announce(self, name):
        helper.add_client(name)

    def list_objects(self):
        return helper.list_objects()

    def get_object_info(self, objname):
        return helper.get_object_info(objname)

    def receive_signal(self, uid, signame, *args, **kwargs):
        helper.receive_signal(uid, signame, *args, **kwargs)


class _FunctionCall(object):
    """Callable stand-in for one remote method on an ``ObjectProxy``."""

    def __init__(self, client, objname, funcname, share_options):
        self._client = client
        self._objname = objname
        self._funcname = funcname
        self._share_options = share_options or {}
        self._cached_result = None

        doc = funcname + _format_argspec_for_doc(self._share_options.get('__argspec__')) + '\n'
        docstr = self._share_options.get('__doc__', '')
        if docstr:
            doc += docstr
        self.__doc__ = doc

    def __call__(self, *args, **kwargs):
        if self._share_options.get('cache_result') and self._cached_result is not None:
            return self._cached_result
        ret = helper.call(self._client, self._objname, self._funcname, *args, **kwargs)
        if self._share_options.get('cache_result'):
            self._cached_result = ret
        return ret


class ObjectProxy(object):
    """
    Client-side proxy for a remote shared object.

    Populated from introspection metadata: methods become ``_FunctionCall``
    instances; properties are placeholders until remote property reads exist.
    """

    _INDEXING_SPECIALS = frozenset(('__getitem__', '__setitem__', '__delitem__'))

    def __init__(self, client, info):
        self._OS_UID = info['uid']
        self._OS_SRV_ID = client
        self._OS_SRV_ADDR = helper.backend.get_addr_for_uid(client)
        self._specials = {}
        self._initialize(info)

    def _call_special(self, name, *args):
        func = self._specials.get(name)
        if func is None:
            if name in self._INDEXING_SPECIALS:
                raise Exception('Object does not support indexing')
            if name == '__contains__':
                raise Exception('Object does not implement __contains__')
            raise Exception(f'Object does not support {name}')
        return func(*args)

    def __getitem__(self, key):
        return self._call_special('__getitem__', key)

    def __setitem__(self, key, val):
        return self._call_special('__setitem__', key, val)

    def __delitem__(self, key):
        return self._call_special('__delitem__', key)

    def __contains__(self, key):
        return self._call_special('__contains__', key)

    def __str__(self):
        s = f'ObjectProxy for {self._OS_UID} @ {self._OS_SRV_ID} (address {self._OS_SRV_ADDR})'
        func = self._specials.get('__str__')
        if func:
            s += f'\nRemote info:\n{func()}'
        return s

    def __repr__(self):
        func = self._specials.get('__str__')
        s = f'ObjectProxy({self._OS_UID})'
        if func:
            s += f': {func()}'
        return s

    def _initialize(self, info):
        if info is None:
            return

        for funcname, share_options in info['functions']:
            # Each remote method becomes a local callable wrapper. Special
            # functions are kept in `_specials` so Python protocols like
            # __getitem__ can still work through normal syntax.
            func = _FunctionCall(self._OS_SRV_ID, self._OS_UID, funcname, share_options)
            if funcname in SPECIAL_FUNCTIONS:
                self._specials[funcname] = func
            else:
                setattr(self, funcname, func)

        # Placeholder: remote property values are not fetched automatically.
        # The object advertises names so attribute access feels natural even
        # though the actual values are still owned by the remote peer.
        for propname in info['properties']:
            setattr(self, propname, 'blaat')

    def connect(self, signame, func):
        return helper.connect_signal(self._OS_UID, signame, func)

    def disconnect(self, hid):
        return helper.disconnect_signal(hid)

    def os_get_client(self):
        return self._OS_SRV_ID

    def os_get_uid(self):
        return self._OS_UID


# Module-level singleton used throughout the lab codebase.
helper = ObjectSharer()
register = helper.register
find_object = helper.find_object

root = RootObject()
register(root, name='root')


# ---------------------------------------------------------------------------
# ZMQ backend and event loop
# ---------------------------------------------------------------------------

class ZMQBackend(object):
    """
    ZeroMQ transport for ObjectSharer.

    One ROUTER socket receives all inbound traffic; each peer gets a DEALER
    socket. The main loop polls ROUTER and dispatches to ``helper.process_message``.
    """

    def __init__(self):
        self.ctx = zmq.Context()
        self.srv = None
        self.addr = None
        self.port = None
        self.timer = None
        self.addr_to_sock_map = {}
        self.addr_to_uid_map = {}
        self.uid_to_addr_map = {}
        self.uid_to_sock_map = {}
        helper.set_backend(self)
        self._timeouts = {}
        self._scheduled_timeouts = []
        self._last_timeout_id = 0

    def get_addr(self):
        """Return the tcp endpoint this instance listens on."""
        if self.addr == '*':
            return f'tcp://127.0.0.1:{int(self.port)}'
        return f'tcp://{self.addr}:{int(self.port)}'

    def start_server(self, addr='*', port=None):
        """Bind the ROUTER socket on *addr*:*port* (random port if port is None)."""
        self.addr = addr
        self.port = port
        self.srv = self.ctx.socket(zmq.ROUTER)
        if port is None:
            self.port = self.srv.bind_to_random_port(
                f'tcp://{addr}', min_port=50000, max_port=60000, max_tries=100,
            )
        else:
            self.srv.bind(f'tcp://{addr}:{int(port)}')
        logger.debug(f'ObjectSharer listening at {self.get_addr()}', )

    def connect_from(self, addr, uid):
        """Associate peer *addr* with ZMQ identity *uid* after handshake."""
        self.addr_to_uid_map[addr] = uid
        self.uid_to_addr_map[uid] = addr
        if addr in self.addr_to_sock_map:
            self.uid_to_sock_map[uid] = self.addr_to_sock_map[addr]

    def connected_to(self, uid):
        return uid in self.uid_to_sock_map

    def get_uid_for_addr(self, addr):
        return self.addr_to_uid_map.get(addr)

    def get_addr_for_uid(self, uid):
        return self.uid_to_addr_map.get(uid)

    def refresh_connection(self, addr):
        self.forget_connection(addr)
        time.sleep(.01)
        self.connect_to(addr)

    def forget_connection(self, addr, remote=True):
        logger.debug(f'Forgetting connection: {addr}', )
        msg = ('goodbye_from', f'tcp://{self.addr}:{int(self.port)}')
        if addr not in self.addr_to_sock_map:
            if remote:
                sock = self.ctx.socket(zmq.DEALER)
                sock.connect(addr)
                sock.send(pickle.dumps(msg))
                sock.close()
            return

        if remote:
            sock = self.addr_to_sock_map[addr]
            sock.send(pickle.dumps(msg))
            sock.close()

        del self.addr_to_sock_map[addr]
        if addr in self.addr_to_uid_map:
            uid = self.addr_to_uid_map.pop(addr)
            self.uid_to_addr_map.pop(uid, None)
            self.uid_to_sock_map.pop(uid, None)

    def _generate_id(self):
        chars = 'abcdefghijklmnopqrstuvwxyz' + 'abcdefghijklmnopqrstuvwxyz'.upper()
        idstr = f'p{int(os.getpid())}_'
        for _ in range(6):
            idstr += chars[random.randint(0, len(chars) - 1)]
        return idstr

    def connect_to(self, addr, delay=1000, async_=False, uid=None):
        """
        Open a DEALER connection to a remote ObjectSharer and complete handshake.

        Sends ``hello_from`` with our listen address; the peer opens a reverse
        connection. The initiator waits for uid resolution via ``AsyncHelloReply``.
        """
        logger.debug(f'Connecting to {addr}', )
        if addr in self.addr_to_sock_map:
            logger.warning(f'Already connected to {addr}', )
            return
        if uid is not None:
            if uid in self.uid_to_addr_map:
                logger.warning(f'Client {uid} already present at different address', )
                return
            # If the caller already knows the peer uid, seed both lookup tables
            # before the hello handshake finishes.
            self.addr_to_uid_map[addr] = uid
            self.uid_to_addr_map[uid] = addr

        sock = self.ctx.socket(zmq.DEALER)
        sock.setsockopt_string(zmq.IDENTITY, self._generate_id())
        sock.connect(addr)
        self.addr_to_sock_map[addr] = sock
        resolved_uid = self.addr_to_uid_map.get(addr)
        if resolved_uid is not None:
            self.uid_to_sock_map[resolved_uid] = sock

        # First message on the new channel announces our listening address.
        # The peer uses that to connect back, giving us bidirectional traffic.
        sock.send(pickle.dumps(('hello_from', f'tcp://{self.addr}:{int(self.port)}')))

        if addr not in self.addr_to_uid_map:
            logger.debug('Waiting for hello reply from server...')
            hello = AsyncHelloReply(addr)
            self.main_loop(delay=delay, wait_for=hello, origin=7)
            if not hello.is_valid():
                raise TimeoutError(f'Connection to {addr} timed out; no reply received')

        if addr not in self.addr_to_uid_map:
            raise Exception('UID not resolved!')
        helper.request_client_proxy(self.addr_to_uid_map[addr], async_=async_)

    def send_to(self, dest, msg, bufs=None):
        """Send pickled *msg* (and optional numpy frames) to peer *dest* (uid)."""
        logger.debug(f'Sending {len(msg)} bytes to {dest}', )
        sock = self.uid_to_sock_map.get(dest)
        if sock is None:
            raise Exception(f'Unable to resolve destination {dest}')

        if bufs is None:
            sock.send(msg)
        else:
            sock.send_multipart([msg] + list(bufs))

        if REDUCE_LATENCY:
            for _ in range(10):
                os.getcwd()

    def timeout_add(self, delay, func, *args):
        """
        Schedule *func* in the main loop. Return True from *func* to repeat
        every *delay* milliseconds.
        """
        self._last_timeout_id += 1
        start = time.time()
        self._timeouts[self._last_timeout_id] = dict(
            start=start, delay=delay / 1000.0, func=func, args=args,
        )
        bisect.insort(self._scheduled_timeouts, (start + delay / 1000.0, self._last_timeout_id))
        return self._last_timeout_id

    def timeout_remove(self, t_id):
        self._timeouts.pop(t_id, None)

    def _run_timeouts(self):
        for _ in range(len(self._scheduled_timeouts)):
            now = time.time()
            if not self._scheduled_timeouts or self._scheduled_timeouts[0][0] >= now:
                break
            t, t_id = self._scheduled_timeouts.pop(0)
            info = self._timeouts.get(t_id)
            if info is None:
                continue
            try:
                if not info['func'](*info['args']):
                    self.timeout_remove(t_id)
                    continue
                now2 = time.time()
                delta = (now2 - t) % info['delay']
                t_new = now2 + info['delay'] - delta
                bisect.insort(self._scheduled_timeouts, (t_new, t_id))
            except Exception as e:
                logger.error(f'Timeout call {int(t_id)} failed: {e!s}', )
                self.timeout_remove(t_id)

    @staticmethod
    def _normalize_wait_for(wait_for):
        if wait_for is None:
            return None
        if isinstance(wait_for, (tuple, list)):
            return list(wait_for)
        return [wait_for]

    def _compute_poll_delay(self, endtime):
        if endtime is not None:
            curdelay = endtime - time.time()
        else:
            curdelay = 10000.0
        if self._scheduled_timeouts:
            to_delay = max(0.0, (self._scheduled_timeouts[0][0] - time.time()) * 1000.0)
            curdelay = min(curdelay, to_delay)
        return curdelay

    def _decode_message(self, msgs):
        try:
            return pickle.loads(msgs[1])
        except Exception as e:
            payload = msgs[1]
            if isinstance(payload, bytes):
                try:
                    preview = payload.decode('unicode-escape')
                except Exception:
                    preview = repr(payload)
            else:
                preview = repr(payload)
            logger.warning(f'Unable to decode object: {e!s} {preview}', )
            return None

    @staticmethod
    def _wait_for_complete(wait_for):
        remaining = []

        for item in wait_for:
            if not item.is_valid():
                remaining.append(item)

        wait_for[:] = remaining

        return len(wait_for) == 0

    def _main_loop(self, delay=None, wait_for=None, origin=0, poll_zmq=True):
        """
        Core receive loop.

        *origin* is a debug tag identifying which caller entered the loop
        (used when tracing timeout issues with Alazar hardware).

        When *poll_zmq* is False (``main_loop_alz``), ZMQ polling is skipped so
        timeouts still run without blocking on socket recv — an Alazar workaround.
        """
        start = time.time()
        endtime = None if delay is None else start + delay / 1000.0
        wait_for = self._normalize_wait_for(wait_for)

        if wait_for is None:
            # If no caller is waiting for a specific reply, process any queued
            # signals before entering the poll loop.
            helper.flush_queue()

        poller = zmq.Poller()
        poller.register(self.srv, flags=zmq.POLLIN)

        while True:
            # Poll duration is driven by the soonest timeout or caller deadline.
            curdelay = self._compute_poll_delay(endtime)
            socks = poller.poll(curdelay) if poll_zmq else []

            if not socks:
                self._run_timeouts()
                if endtime is not None and time.time() >= endtime:
                    return False
                continue

            msgs = self.srv.recv_multipart()
            client = msgs[0]
            info = self._decode_message(msgs)
            if info is None:
                return

            try:
                logger.debug(f'Starting Message processing {info!s}', )
                helper.process_message(client, info, msgs[2:], waiting=(wait_for is not None))
            except Exception as e:
                logger.warning(f'Failed to process message: {e!s}\n{traceback.format_exc()}', )
            finally:
                logger.debug(f'Message processed {info!s}', )

            if wait_for is not None and self._wait_for_complete(wait_for):
                # Synchronous call path: return as soon as the awaited reply has
                # been marked valid by _handle_return().
                return True

            if endtime is not None and time.time() >= endtime:
                return False

    def main_loop(self, delay=None, wait_for=None, origin=0):
        """
        Run the receiving main loop for at most *delay* msec.

        If *wait_for* is set, return True once every object in the list reports
        valid via ``is_valid()``, or False on timeout.
        """
        return self._main_loop(delay=delay, wait_for=wait_for, origin=origin, poll_zmq=True)

    def main_loop_alz(self, delay=None, wait_for=None, origin=0):
        """
        Alazar-specific main loop: same as ``main_loop`` but without ZMQ polling.

        Kept for API compatibility; ZMQ recv was hanging inside Alazar calls.
        """
        return self._main_loop(delay=delay, wait_for=wait_for, origin=origin, poll_zmq=False)

    def _qt_timer(self):
        self.main_loop(delay=0)
        return True

    def add_qt_timer(self, interval=20):
        """
        Install a QTimer so ZMQ messages are processed inside the Qt event loop.
        """
        if self.timer is not None:
            logger.warning('Timer already installed')
            return False

        from PyQt5 import QtCore
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            logger.warning('No QApplication instance; create one before add_qt_timer()')
            return False
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._qt_timer)
        self.timer.start(interval)
        return True
