import os
from typing import Mapping, Union, get_type_hints

from dotenv import dotenv_values


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

    def __init__(self, env: Mapping[str, str]):
        self.load(env)

    def load(self, env: Mapping[str, str]) -> None:
        """依 env 重新設定所有欄位，env 沒有提供的欄位還原為預設值

        任一欄位無法轉型時拋出 AppConfigError，且不會修改任何欄位。

        Args:
            env (Mapping[str, str]): 欄位名稱（全大寫）對應的設定值
        """
        # Read annotations from the class: since Python 3.14 (PEP 649) instances no longer expose them
        type_hints = get_type_hints(type(self))
        values = {}
        for field in type_hints:
            if not field.isupper():
                continue

            # Raise AppConfigError if required field not supplied
            # 預設值取自類別，避免重複 load 時沿用上一次的設定
            default_value = getattr(type(self), field, None)
            if default_value is None and env.get(field) is None:
                raise AppConfigError('The {} field is required'.format(field))

            # Cast env var value to expected type and raise AppConfigError on failure
            try:
                var_type = type_hints[field]
                if var_type == bool:
                    value = _parse_bool(env.get(field, default_value))
                else:
                    value = var_type(env.get(field, default_value))
            except ValueError:
                raise AppConfigError('Unable to cast value of "{}" to type "{}" for "{}" field'.format(
                    env[field],
                    var_type,
                    field
                ))
            values[field] = value

        for field, value in values.items():
            setattr(self, field, value)

    def __repr__(self):
        return str(self.__dict__)


# Expose Config object for app to import
# import 時只使用預設值；讀取設定檔由呼叫端以 load_config() 決定
Config = AppConfig({})


def load_config(path: Union[str, os.PathLike], env: Union[Mapping[str, str], None] = None) -> AppConfig:
    """讀取 ini 設定檔並更新 Config

    設定檔中的 [Section] 標頭會被忽略，鍵名不分大小寫。env 中的同名變數優先於設定檔。
    設定檔不存在時只套用 env 與預設值。

    會直接修改既有的 Config 物件（不建立新物件），各模組 import 的 Config 都會看到新設定。

    Args:
        path (str | os.PathLike): 設定檔路徑
        env (Mapping[str, str] | None): 覆寫用的環境變數，預設為 os.environ

    Returns:
        AppConfig: 更新後的 Config
    """
    if env is None:
        env = os.environ
    values = {
        key.upper(): value
        for key, value in dotenv_values(path).items()
        if value is not None
    }
    values.update({key.upper(): value for key, value in env.items()})
    Config.load(values)
    return Config
