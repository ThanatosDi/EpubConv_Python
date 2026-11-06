import os
import pathlib
from contextlib import contextmanager
from typing import Iterator, Union

from loguru import logger

from epubconv.config import Config
from epubconv.enums.converter_enum import Converter
from epubconv.enums.engine_enum import EngineEnum
from epubconv.enums.format_enum import FormatEnum
from epubconv.modules.epubconv import EPUBConv


def convert_epub(
    epub_path: Union[str, os.PathLike],
    *,
    engine: Union[str, None] = None,
    converter: Union[str, None] = None,
    format: Union[str, None] = None,  # pylint: disable=redefined-builtin
    add_suffix: Union[bool, None] = None,
) -> pathlib.Path:
    """轉換一本 epub，回傳輸出 epub 的路徑

    未指定的選項沿用 Config 目前的設定（預設值，或 load_config() 讀入的設定檔）。
    指定的選項只在這次轉換生效，結束後還原 Config。

    Config 是全域物件，同一個程序同時只能執行一個轉換，不可在多個執行緒平行呼叫。

    Args:
        epub_path (str | os.PathLike): epub 檔案路徑
        engine (str | None): 轉換引擎，見 EngineEnum
        converter (str | None): 轉換器，見 Converter
        format (str | None): 書寫方向，見 FormatEnum
        add_suffix (bool | None): 輸出檔名是否加上 _<converter> 後綴

    Returns:
        pathlib.Path: 輸出 epub 的路徑

    Raises:
        FileNotFoundError: epub 檔案不存在
        ValueError: 引擎、轉換器或書寫方向不受支援
    """
    overrides = {
        'ENGINE': engine,
        'CONVERTER': converter,
        'FORMAT': format,
        'ADD_SUFFIX': add_suffix,
    }
    with _override_config({k: v for k, v in overrides.items() if v is not None}):
        _validate_config()
        return _convert(pathlib.Path(epub_path).resolve())


@contextmanager
def _override_config(overrides: dict) -> Iterator[None]:
    """暫時覆寫 Config 的欄位，離開時還原"""
    original = {key: getattr(Config, key) for key in overrides}
    try:
        for key, value in overrides.items():
            setattr(Config, key, value)
        yield
    finally:
        for key, value in original.items():
            setattr(Config, key, value)


def _validate_config() -> None:
    """在解壓縮前檢查設定，避免轉換到一半才失敗"""
    if not EngineEnum.has_value(Config.ENGINE):
        raise ValueError(f'engine "{Config.ENGINE}" is not in EngineEnum')
    if not Converter.has_name(Config.CONVERTER):
        raise ValueError(f'converter "{Config.CONVERTER}" is not in Converter')
    if not FormatEnum.has_value(Config.FORMAT):
        raise ValueError(f'format "{Config.FORMAT}" is not in FormatEnum')


def _convert(epub_path: pathlib.Path) -> pathlib.Path:
    if not epub_path.is_file():
        raise FileNotFoundError(f'找不到 epub 檔案: {epub_path}')
    epubconv = EPUBConv(str(epub_path))
    try:
        epubconv.epub_extract()
        epub_file = epubconv.epub_file
        content_files = epub_file.content_files
        css_files = epub_file.css_files
        opf_file = epub_file.opf_file
        epubconv.content_convert(content_files)
        epubconv.opf_convert(opf_file)
        epubconv.file_rename(content_files)
        epubconv.writing_format(
            opf_path=opf_file,
            epub_extract_path=epubconv.epub_extract_path,
            css_files=css_files,
            content_files=content_files
        )
        output_path = epubconv.epub_compress()
    finally:
        # 轉換失敗時也要刪除解壓縮的暫存資料夾
        if os.path.isdir(epubconv.epub_extract_path):
            epubconv.clean()
    logger.info(f'輸出 epub: {output_path}')
    return output_path
