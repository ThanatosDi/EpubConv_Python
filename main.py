"""命令列／exe 入口：把 epub 拖曳到 EpubConv.exe 上即可轉換

config.ini 與日誌都放在 exe（或 main.py）所在的目錄，與工作目錄無關。
"""
import os
import sys
from pathlib import Path

from loguru import logger

from epubconv import __VERSION__, Config, convert_epub, load_config

BANNER = rf'''
  ______             _      _____
 |  ____|           | |    / ____|
 | |__   _ __  _   _| |__ | |     ___  _ ____   __
 |  __| | '_ \| | | | '_ \| |    / _ \| '_ \ \ / /
 | |____| |_) | |_| | |_) | |___| (_) | | | \ V /
 |______| .__/ \__,_|_.__/ \_____\___/|_| |_|\_/
        | |
        |_|
 v{__VERSION__}'''


def base_dir() -> Path:
    """exe 或 main.py 所在的目錄"""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def setup_logger(log_dir: Path) -> None:
    """輸出日誌到主控台與 log_dir"""
    handlers = [
        {
            "sink": str(log_dir / 'app_{time:YYYY-MM-DD}.log'),
            "level": Config.LOGLEVEL.upper(),
            "format": '{time} {level} {message}',
            "rotation": '00:00',
            "enqueue": True
        }
    ]
    # 打包成無主控台的程式時 sys.stdout 為 None
    if sys.stdout is not None:
        handlers.insert(0, {"sink": sys.stdout, "level": Config.STDLEVEL.upper()})
    logger.configure(handlers=handlers)


def main(epub_paths: list[str]) -> None:
    root = base_dir()
    load_config(root / 'config.ini')
    setup_logger(root / 'storages' / 'logs')
    logger.info(BANNER)
    logger.debug(Config)
    for epub_path in epub_paths:
        convert_epub(epub_path)
    if Config.ENABLE_PAUSE:
        os.system('pause')


if __name__ == '__main__':
    main(sys.argv[1:])
