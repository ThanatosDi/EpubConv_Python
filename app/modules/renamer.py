import logging
import os

logger = logging.getLogger('ReNamer')


class ReNamer():
    def __init__(self, file_absolute_path: str):
        self.file_absolute_path = file_absolute_path

    def __delete_original_file(self) -> None:
        logger.debug(f'删除原始檔案: {os.path.basename(self.file_absolute_path)}')
        os.remove(self.file_absolute_path)

    def __rename_converted_file(self) -> None:
        logger.debug(
            f'重新命名: {os.path.basename(self.file_absolute_path)}.new -> {os.path.basename(self.file_absolute_path)}')
        os.rename(self.file_absolute_path+'.new', self.file_absolute_path)

    def rename(self) -> None:
        """刪除原始檔案並將轉換後的檔案重新命名為原始檔案名稱
        """
        self.__delete_original_file()
        self.__rename_converted_file()
