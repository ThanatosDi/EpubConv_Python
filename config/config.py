import os
import sys
from typing import Union, get_type_hints

import dotenv

basedir = os.path.dirname(sys.argv[0])
# when run via python main.py xxx
#  basedir is "", and at which time, no need to chdir
if basedir != "":
    os.chdir(basedir)

_path = "config.ini"
if os.name == 'nt':
    dotenv.load_dotenv(_path)
else:
    d = dotenv.dotenv_values(_path)
    _ENV = os.environ
    for k, v in d.items():
        if v is not None:
            _ENV[k.upper()] = v
    del d, _ENV
del _path

class AppConfigError(Exception):
    pass


def _parse_bool(val: Union[str, bool]) -> bool:  # pylint: disable=E1136
    return val if isinstance(val, bool) else val.lower() in ['true', 'yes', '1']

# AppConfig class with required fields, default values, type checking, and typecasting for int and bool values


class AppConfig:
    ENGINE: str = 'opencc'
    CONVERTER: str = 's2t'
    FORMAT: str = 'horizontal'
    LOGLEVEL: str = 'INFO'
    STDLEVEL: str = 'INFO'
    ASYNC_LIMIT: int = 5
    ASYNC_LIMIT_PER_HOST: int = 10
    FILE_CHECK: bool = False
    ENABLE_PAUSE: bool = False
    ADD_SUFFIX: bool = True

    """
    Map environment variables to class fields according to these rules:
      - Field won't be parsed unless it has a type annotation
      - Field will be skipped if not in all caps
      - Class field and environment variable name are the same
    """

    def __init__(self, env):
        for field in self.__annotations__:
            if not field.isupper():
                continue

            # Raise AppConfigError if required field not supplied
            default_value = getattr(self, field, None)
            if default_value is None and env.get(field) is None:
                raise AppConfigError('The {} field is required'.format(field))

            # Cast env var value to expected type and raise AppConfigError on failure
            try:
                var_type = get_type_hints(AppConfig)[field]
                if var_type == bool:
                    value = _parse_bool(env.get(field, default_value))
                else:
                    value = var_type(env.get(field, default_value))

                self.__setattr__(field, value)
            except ValueError:
                raise AppConfigError('Unable to cast value of "{}" to type "{}" for "{}" field'.format(
                    env[field],
                    var_type,
                    field
                ))

    def __repr__(self):
        return str(self.__dict__)


# Expose Config object for app to import
Config = AppConfig(os.environ)
