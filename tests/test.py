import string
import unicodedata

def classify_character(c):
    """单个字符分类"""
    if len(c) != 1:
        raise ValueError("输入必须是单个字符")
    
    code = ord(c)
    if (0x3040 <= code <= 0x309F) or \
        (0x30A0 <= code <= 0x30FF) or \
        (0xFF65 <= code <= 0xFF9F):
        return "假名"
    if (0x0041 <= code <= 0x005A) or (0x0061 <= code <= 0x007A):
        return "字母"
    if c in string.punctuation:
        return "标点符号"
    category = unicodedata.category(c)
    if category in {'Po', 'Pd', 'Ps', 'Pe', 'Pi', 'Pf', 'Pc'}:
        return "标点符号"
    return "其他"
a="!！,，、;；:：~-—…－·.｡。()（）[]【】「」『』?？azAZｱｦあをアヲ"
for i in a:
    print(i, classify_character(i))