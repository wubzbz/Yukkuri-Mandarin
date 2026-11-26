"""公共 API：把输入文本转换为假名拟音。

`Converter` 持有运行时资源（数据库连接、分词器），适合批量转换；
顶层 `text_convert` / `pinyin_convert` 是单次调用的便捷入口。
"""

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING, Optional

from .db import PinyinRepository, SchemaError
from .phonology.pinyin import build_serial
from .phonology.sandhi import apply as apply_sandhi
from .pipeline import assemble, fill_kana, fill_pinyin, finalize, normalize_text
from .segments import Document
from .settings import DEFAULT_CONFIG, Config

if TYPE_CHECKING:
    from jieba import Tokenizer

# 拼音输入里的 ASCII 标点 → 输出标点
_PUNCTUATION = {",": "、", ".": "。", ";": ",", "?": "?"}


class Converter:
    """持有配置与运行时资源的转换器。

    数据库连接与分词器都是懒加载的；用一个实例连续转换多条文本时，
    连接只会打开一次。实例不是线程安全的，每个线程应各用一个。
    """

    def __init__(
        self,
        config: Config = DEFAULT_CONFIG,
        tokenizer: Optional["Tokenizer"] = None,
    ) -> None:
        """构造转换器。

        Args:
            config: 转换配置。
            tokenizer: jieba 分词器；None 时在首次转换时创建默认分词器。
        """
        self._config = config
        self._tokenizer = tokenizer
        self._tokenizer_ready = tokenizer is not None
        self._repository: Optional[PinyinRepository] = None

    @property
    def config(self) -> Config:
        """当前配置。"""
        return self._config

    @property
    def tokenizer(self) -> Optional["Tokenizer"]:
        """分词器；未安装 jieba 时为 None。"""
        if not self._tokenizer_ready:
            self._tokenizer = _default_tokenizer()
            self._tokenizer_ready = True
        return self._tokenizer

    @property
    def repository(self) -> PinyinRepository:
        """拼音数据库仓储；首次访问时打开。

        内置库始终只读；自定义库优先只读打开，若 schema 落后则先迁移一次。
        """
        if self._repository is None:
            path = self._config.database
            if path is None:
                self._repository = PinyinRepository.open()
            else:
                try:
                    self._repository = PinyinRepository.open(path, readonly=True)
                except SchemaError:
                    with PinyinRepository.open(path):
                        pass
                    self._repository = PinyinRepository.open(path, readonly=True)
        return self._repository

    def close(self) -> None:
        """关闭数据库连接；可重复调用。"""
        if self._repository is not None:
            self._repository.close()
            self._repository = None

    def __enter__(self) -> "Converter":
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        self.close()

    def text_convert(self, sentence: str, *, without_accent: bool = False) -> str:
        """将中文句子转换为伪日本语。

        Args:
            sentence: 输入的句子。
            without_accent: 是否去除音声记号。

        Returns:
            转换后的句子。

        Raises:
            ValueError: sentence 不是字符串。
        """
        _check_sentence(sentence)
        if not sentence:
            return ""
        document = Document.from_text(normalize_text(sentence))
        # 没有汉字段时不碰分词器和数据库
        if any(run.kind == "hanzi" for run in document.runs):
            document = fill_pinyin(document, self.tokenizer)
            document = apply_sandhi(document)
            document = fill_kana(document, self.repository)
        result = assemble(
            document,
            self._config.non_hanzi,
            without_accent=without_accent,
        )
        return result

    def pinyin_convert(
        self,
        sentence: str,
        *,
        error: str = "",
        without_accent: bool = False,
    ) -> str:
        """将拼音序列转换为伪日本语。

        Args:
            sentence: 以空格分隔的拼音，音节末尾带 0–5 的声调数字
                （0 视作轻声）。
            error: 查询无结果时的返回值；传 ``"keep"`` 时保留原音节。
            without_accent: 是否去除音声记号。

        Returns:
            转换后的句子。

        Raises:
            ValueError: sentence 不是字符串。
        """
        _check_sentence(sentence)
        if not sentence:
            return ""
        serial = build_serial(_parse_pinyin_tokens(sentence))
        entries = self.repository.get_many(
            [(syllable, tones) for syllable, tones in serial]
        )
        parts = []
        for (syllable, tones), entry in zip(serial, entries):
            if tones[1] == "0":
                parts.append(_PUNCTUATION.get(syllable, error))
            elif entry is not None:
                parts.append(entry.hiragana)
            elif error == "keep":
                parts.append(syllable)
            else:
                parts.append(error)
        return finalize("".join(parts), without_accent=without_accent)


def text_convert(
    sentence: str,
    *,
    without_accent: bool = False,
    config: Config = DEFAULT_CONFIG,
    tokenizer: Optional["Tokenizer"] = None,
) -> str:
    """单次转换的便捷入口，等价于临时创建一个 Converter。

    Args:
        sentence: 输入的句子。
        without_accent: 是否去除音声记号。
        config: 转换配置。
        tokenizer: jieba 分词器；None 时使用默认分词器。

    Returns:
        转换后的句子。
    """
    with Converter(config, tokenizer) as converter:
        return converter.text_convert(sentence, without_accent=without_accent)


def pinyin_convert(
    sentence: str,
    *,
    error: str = "",
    without_accent: bool = False,
    config: Config = DEFAULT_CONFIG,
) -> str:
    """单次拼音转换的便捷入口，等价于临时创建一个 Converter。

    Args:
        sentence: 以空格分隔的拼音。
        error: 查询无结果时的返回值。
        without_accent: 是否去除音声记号。
        config: 转换配置。

    Returns:
        转换后的句子。
    """
    with Converter(config) as converter:
        return converter.pinyin_convert(
            sentence, error=error, without_accent=without_accent
        )


def _parse_pinyin_tokens(sentence: str) -> list[tuple[str, int]]:
    """把拼音输入拆成 (音节, 声调)；无调数字的片段视为标点（声调 0）。"""
    tokens: list[tuple[str, int]] = []
    for token in sentence.split():
        if token and token[-1] in "012345":
            tone = int(token[-1])
            # 输入里的 0 视作轻声 5；真正的标点 token 没有声调数字
            tokens.append((token[:-1], 5 if tone == 0 else tone))
        else:
            tokens.append((token, 0))
    return tokens


# 默认分词器进程内共享；jieba 首次分词要加载词典，不能每个 Converter 建一个
_TOKENIZER_LOCK = threading.Lock()
_DEFAULT_TOKENIZER: Optional["Tokenizer"] = None
_TOKENIZER_INITIALIZED = False


def _default_tokenizer() -> Optional["Tokenizer"]:
    """返回进程内共享的默认分词器；未安装 jieba 时返回 None。"""
    global _DEFAULT_TOKENIZER, _TOKENIZER_INITIALIZED
    if _TOKENIZER_INITIALIZED:
        return _DEFAULT_TOKENIZER
    with _TOKENIZER_LOCK:
        if not _TOKENIZER_INITIALIZED:
            _DEFAULT_TOKENIZER = _create_tokenizer()
            _TOKENIZER_INITIALIZED = True
    return _DEFAULT_TOKENIZER


def _create_tokenizer() -> Optional["Tokenizer"]:
    """创建分词器；未安装 jieba 时返回 None。"""
    try:
        import jieba
        from jieba import Tokenizer
    except ImportError:
        return None
    # 默认分词器加载词典时会输出 INFO 级日志，这里压到 WARNING
    jieba.setLogLevel(logging.WARNING)
    return Tokenizer()


def _check_sentence(sentence: str) -> None:
    """校验输入类型。"""
    if not isinstance(sentence, str):
        raise ValueError(f"参数sentence必须是字符串: {sentence}")
