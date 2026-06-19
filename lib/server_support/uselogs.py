# lib/server_support/uselogs.py
#
# .env-driven logging configuration for the instrument server processes.
#
# instrument_server.py (per-instrument subprocess) and instruments_server.py
# (the coordinator) each hardcoded `logging.getLogger().setLevel(logging.INFO)`,
# which silently swallowed every logger.debug() call from instrument plugins
# (e.g. Keysight_DIG's _log_status diagnostics) — DEBUG < INFO never reaches a
# handler. This moves that decision into a repo-root .env file so individual
# modules (by logger name, i.e. __name__) can be bumped to DEBUG without
# touching code or drowning everything else in noise.
#
# .env format (KEY=VALUE per line, '#' comments, blank lines ignored):
#   LOG_DEFAULT=INFO
#   LOG_Keysight_DIG=DEBUG
#   LOG_Keysight_AWG=INFO
#
# LOG_DEFAULT sets the root logger's level. LOG_<name> sets the level of
# logging.getLogger(<name>) — <name> is the logger's __name__, e.g. the
# instrument plugin module name ("Keysight_DIG") for plugin loggers.
#
# A real environment variable of the same name always overrides the .env
# file (dotenv_values does not touch os.environ, so we merge it ourselves).

import logging
import os

from dotenv import dotenv_values

_PREFIX = 'LOG_'
_DEFAULT_KEY = _PREFIX + 'DEFAULT'

# Repo root .env, sitting next to create_instruments.py.
_ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), '.env')


def load_log_levels(env_path=_ENV_PATH):
    """Return {logger_name: level_name} from .env, with real env vars taking precedence.

    'root' is a special logger_name meaning the root logger (from LOG_DEFAULT).
    """
    raw = {k: v for k, v in dotenv_values(env_path).items() if v is not None}
    raw.update({k: v for k, v in os.environ.items() if k.startswith(_PREFIX)})

    levels = {}
    for key, value in raw.items():
        if not key.startswith(_PREFIX):
            continue
        name = key[len(_PREFIX):]
        levels['root' if name == 'DEFAULT' else name] = value
    return levels


def configure_logging(env_path=_ENV_PATH, fallback_default=logging.INFO):
    """Apply .env-driven log levels. Call once near the top of a server entrypoint.

    Sets the root logger's level (LOG_DEFAULT, or <fallback_default> if
    unset) and then sets per-module levels (LOG_<name>) on top.
    """
    logging.basicConfig()  # no-op if a handler is already attached

    levels = load_log_levels(env_path)

    root_level = levels.pop('root', None)
    logging.getLogger().setLevel(
        getattr(logging, root_level.upper(), fallback_default) if root_level else fallback_default
    )

    for name, level_name in levels.items():
        level = getattr(logging, level_name.upper(), None)
        if level is None:
            logging.getLogger().warning(
                'uselogs: ignoring invalid level %r for logger %r', level_name, name
            )
            continue
        logging.getLogger(name).setLevel(level)
