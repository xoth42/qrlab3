# visafunc.py, NI VISA support functions.
# Reinier Heeres <reinier@heeres.eu>, 2009
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

import time
import logging

from pyvisa import constants


def _get_bytes_available(visains):
    """Return the number of bytes currently waiting in the input buffer."""
    if hasattr(visains, 'bytes_in_buffer'):
        return int(visains.bytes_in_buffer)

    if hasattr(visains, 'get_visa_attribute'):
        try:
            return int(visains.get_visa_attribute(constants.VI_ATTR_ASRL_AVAIL_NUM))
        except Exception:
            pass

    if hasattr(visains, 'in_waiting'):
        return int(visains.in_waiting)

    raise RuntimeError('Could not determine how many bytes are available')


def _read_bytes(visains, nbytes):
    """Read exactly ``nbytes`` from a VISA resource and return bytes."""
    if hasattr(visains, 'read_bytes'):
        data = visains.read_bytes(nbytes)
    elif hasattr(visains, 'read_raw'):
        data = visains.read_raw()
        data = data[:nbytes]
    else:
        data = visains.read(nbytes)

    if isinstance(data, str):
        data = data.encode('latin1')
    return data

def get_navail(visains):
    '''
    Return number of bytes available to read from visains.
    '''

    return _get_bytes_available(visains)

def wait_data(visains, nbytes=1, maxdelay=1.0):
    '''
    Wait for maxdelay seconds for data available to read from visains.
    The loop consist of 1msec delays.
    '''
    deadline = time.monotonic() + maxdelay
    for _ in range(int(maxdelay * 1000) + 1):
        if get_navail(visains) >= nbytes:
            return True
        if time.monotonic() >= deadline:
            break
        time.sleep(0.001)
    return False

def readn(visains, n):
    return _read_bytes(visains, n)


def read_all(visains):
    """
    Read all available data from the input buffer of visains.
    """

    buf = bytearray()
    try:
        for blen in iter(lambda: get_navail(visains), 0):
            buf.extend(_read_bytes(visains, blen))
    except Exception:
        # Preserve the historical behavior of returning partial data instead of
        # failing the whole read when the resource reports an unexpected state.
        logging.exception("Exception occurred while reading all available data from visains")

    return bytes(buf)
