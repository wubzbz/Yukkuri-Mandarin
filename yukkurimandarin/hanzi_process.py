# 处理汉字片段。

from typing import List, Tuple, Optional
from pypinyin import pinyin, Style

from yukkurimandarin.database_mngr import DatabaseManager

# 可选组件
try:
    import jieba
    from jieba import Tokenizer
    _HAS_JIEBA = True
except ImportError:
    _HAS_JIEBA = False


def hanzi_process(fragments: List[str], tokenizer: Optional["jieba.Tokenizer"], db_mngr: Optional[DatabaseManager]) -> List[str]:
    """
    处理汉字片段

    Args:
        fragments: 汉字片段
        tokenizer: jieba分词器
        db_mngr: 拼音数据库管理类

    Returns:
        处理结果
    """
    if not fragments:
        return []
    # 标记片段的分隔点：音节为斜杠，声调为0
    mark = "/0"
    marked_frag = [mark]
    for f in fragments:
        marked_frag.append(f)
        marked_frag.append(mark)
    # 分词
    marked_frag = tokenize(marked_frag, tokenizer=tokenizer, mark=mark)
    #print(marked_frag)
    # 拼音化
    pinyin_list = pinyin(marked_frag, style=Style.TONE3, neutral_tone_with_five=True)
    # 处理连续上声
    modify_consecutive_threes(pinyin_list)
    #print(pinyin_list)
    # 构造拼音序列
    serial: List[Tuple[str, str]] = []
    for i in range(1, len(pinyin_list)-1):
        serial.append((pinyin_list[i][0][:-1], f"{pinyin_list[i-1][0][-1]}{pinyin_list[i][0][-1]}{pinyin_list[i+1][0][-1]}"))
    # 查询假名拟音
    if db_mngr is None:
        db_mngr = DatabaseManager()
    hiragana_list = db_mngr.serial_search(serial, "")
    # 还原fragments结构
    result = []
    frag = []
    for i, entry in enumerate(serial):
        # 当字是片段的结束时
        if entry[0] == "/" and entry[1][1] == "0":
            result.append("".join(frag))
            frag.clear()
        else:
            frag.append(hiragana_list[i])
    # 加入最后一个片段
    result.append("".join(frag))
    # 检查长度是否不变
    if len(result) != len(fragments):
        raise ValueError("处理结果出错")
    return result


def tokenize(fragments: List[str], tokenizer: Optional["jieba.Tokenizer"], mark: str = "/0") -> List[str]:
    """使用jieba对片段列表进行分词
    
    Args:
        fragments: 需要分词的片段列表
        mark: 片段分隔符
        tokenizer: jieba分词器
    
    Returns:
        分词后的列表
    """
    if not _HAS_JIEBA:
        return fragments
    if tokenizer is None:
        tokenizer = Tokenizer()
    # 遍历列表中的每个句子，对每个句子进行分词
    result: List[str] = []
    for fragment in fragments:
        if fragment == mark:
            result.append(mark)
        else:
            result.extend(tokenizer.lcut(fragment)) 
    return result


def modify_consecutive_threes(pinyin_list: List[List[str]]) -> None:
    """
    处理连续上声的变调。采用简化的两字组和三字组组合模式。
    - 此函数直接修改传入的列表
    """
    # 遍历的索引
    i = 0
    # 首个两字组：0；三字组：1；两字组：2。
    flag = 0
    for i in range(len(pinyin_list)):
        if pinyin_list[i][0][-1] == "3" and pinyin_list[i+1][0][-1] == "3":
            if flag == 0:
                flag = 1
            elif flag == 1:
                flag = 2
            elif flag == 2:
                pinyin_list[i-1][0] = f"{pinyin_list[i-1][0][:-1]}3"
                flag = 1
            else:
                raise ValueError(f"flag不正确：{flag}")
            pinyin_list[i][0] = f"{pinyin_list[i][0][:-1]}2"
        else:
            if flag != 0:
                flag = 0
    return