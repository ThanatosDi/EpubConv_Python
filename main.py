import os
import sys

from loguru import logger

from app import __VERSION__
from app.modules.epubconv import EPUBConv
from config.config import Config

logger.configure(
    handlers=[
        {"sink": sys.stdout, "level": Config.STDLEVEL.upper()},
        {
            "sink": 'storages/logs/app_{time:YYYY-MM-DD}.log',
            "level": Config.LOGLEVEL.upper(),
            "format": '{time} {level} {message}',
            "rotation": '00:00',
            "enqueue": True
        }
    ]
)

logger.info(
    f'''
  ______             _      _____
 |  ____|           | |    / ____|
 | |__   _ __  _   _| |__ | |     ___  _ ____   __
 |  __| | '_ \| | | | '_ \| |    / _ \| '_ \ \ / /
 | |____| |_) | |_| | |_) | |___| (_) | | | \ V /
 |______| .__/ \__,_|_.__/ \_____\___/|_| |_|\_/
        | |
        |_|
 v{__VERSION__}'''
)

logger.debug(Config)

if __name__ == '__main__':
    for epub_path in sys.argv[1:]:
        epubconv = EPUBConv(epub_path)
        epubconv.epub_extract()
        content_files = epubconv.epub_file.content_files
        css_files = epubconv.epub_file.css_files
        opf_file = epubconv.epub_file.opf_file
        epubconv.content_convert(content_files)
        epubconv.opf_convert(opf_file)
        epubconv.file_rename(content_files)
        epubconv.writing_format(
            opf_path=opf_file,
            epub_extract_path=epubconv.epub_extract_path,
            css_files=css_files,
            content_files=content_files
        )
        epubconv.epub_compress()
        epubconv.clean()
    if Config.ENABLE_PAUSE:
        os.system('pause')
