class FileTypeError(Exception):
    pass


class FileUnzipError(Exception):
    pass


class ConfigError(Exception):
    pass


class RequestError(Exception):
    pass


class ZhconvertKeyNotFound(Exception):
    def __init__(self, error_keys):
        self.error_keys = error_keys

    def __str__(self):
        return f'Parameter key not found. {self.error_keys} not allow key.'


class ZhConvertMissNecessarykey(Exception):
    def __str__(self):
        return f'Miss necessary key "text" or "converter".'

class ZhConvertError(Exception):
    def __str__(self):
        return f'ZhConvert response is None, please check text or converter.'
