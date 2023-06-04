import os
import logging

logger = logging.getLogger('ReNamer')


class ReNamer():
    def __init__(self, fileAbsolutePath: str):
        self.fileAbsolutePath = fileAbsolutePath

    def __delete_original_file(self) -> None:
        logger.debug(f'删除原始檔案: {os.path.basename(self.fileAbsolutePath)}')
        os.remove(self.fileAbsolutePath)

    def __rename_converted_file(self) -> None:
        logger.debug(
            f'重新命名: {os.path.basename(self.fileAbsolutePath)}.new -> {os.path.basename(self.fileAbsolutePath)}')
        os.rename(self.fileAbsolutePath+'.new', self.fileAbsolutePath)

    def rename(self) -> None:
        """刪除原始檔案並將轉換後的檔案重新命名為原始檔案名稱
        """
        self.__delete_original_file()
        self.__rename_converted_file()
