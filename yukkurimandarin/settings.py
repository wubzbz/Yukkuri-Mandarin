# 定义参数对象

from typing import Union, Callable


class NonHanziModes:
    """
    设置如何处理各类非汉字字符

    参数种类:
        mode: 处理模式

            - `ignore`: 忽略掉非汉字片段
            - `keep`: 保留非汉字片段
            - `replace`: 用自定义字符串代替非汉字片段
            - 可调用的函数：用于处理非汉字片段

        replace: 仅当mode为 `replace` 时此参数有效。将所有非汉字片段替换为该字符串。
    """
    def __init__(self, 
                 global_mode: Union[str, Callable[[str], str]] = "ignore",
                 global_replace: str = "",
                 en_mode: Union[str, Callable[[str], str], None] = None,
                 en_replace: Union[str, None] = None,
                 ja_mode: Union[str, Callable[[str], str], None] = None,
                 ja_replace: Union[str, None] = None,
                 pc_mode: Union[str, Callable[[str], str], None] = None,
                 pc_replace: Union[str, None] = None,
                 other_mode: Union[str, Callable[[str], str], None] = None,
                 other_replace: Union[str, None] = None,) -> None:
        
        self.en_mode = en_mode if en_mode is not None else global_mode
        self.en_replace = en_replace if en_replace is not None else global_replace
        self.ja_mode = ja_mode if ja_mode is not None else global_mode
        self.ja_replace = ja_replace if ja_replace is not None else global_replace
        self.pc_mode = pc_mode if pc_mode is not None else global_mode
        self.pc_replace = pc_replace if pc_replace is not None else global_replace
        self.other_mode = other_mode if other_mode is not None else global_mode
        self.other_replace = other_replace if other_replace is not None else global_replace