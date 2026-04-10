import pytest
from pypinyin import pinyin, Style

import yukkurimandarin.hanzi_process as t


@pytest.mark.parametrize("input, expected", [
    ([], []),
    ([""], []), # 潜在问题：空字符串消失，可能影响片段合并。
    (["/0"], [["/0"]]),
    (["/0", "高等数学", "/0"], 
     [['/0'], ['gao1'], ['deng3'], ['shu4'], ['xue2'], ['/0']]),
    (["/0", "我很想你跑起来", "/0", "进入蒙古展览馆", "/0"], 
     [['/0'], ['wo2'], ['hen3'], ['xiang2'], ['ni3'], ['pao2'], ['qi3'], ['lai2'], ['/0'], 
      ['jin4'], ['ru4'], ['meng2'], ['gu2'], ['zhan3'], ['lan2'], ['guan3'], ['/0']]), # TODO：某些词语拼音有误，需要加载补丁词典
])
def test_consecutive_threes(input, expected):
    pinyin_list = pinyin(input, style=Style.TONE3, neutral_tone_with_five=True)
    t. modify_consecutive_threes(pinyin_list)
    assert pinyin_list == expected


@pytest.mark.parametrize("input_fragments, expected_pinyin", [
    ([], []),
    (["/0"], [["/0"]]),
    (["/0", "不对", "/0"],
     [["/0"], ["bu2"], ["dui4"], ["/0"]]),
    (["/0", "不好", "/0"],
     [["/0"], ["bu4"], ["hao3"], ["/0"]]),
    (["/0", "不", "好", "不", "对", "/0"],
     [["/0"], ["bu4"], ["hao3"], ["bu2"], ["dui4"], ["/0"]]),
    (["/0", "好", "不", "/0"],
     [["/0"], ["hao3"], ["bu4"], ["/0"]]),
    (["/0", "部", "队", "/0"],
     [["/0"], ["bu4"], ["dui4"], ["/0"]]),
    (["/0", "不要", "/0"],
     [["/0"], ["bu2"], ["yao4"], ["/0"]]),
    (["/0", "不", "/0", "对", "/0"],
     [["/0"], ["bu4"], ["/0"], ["dui4"], ["/0"]]),
])
def test_modify_bu_tone(input_fragments, expected_pinyin):
    mark = "/0"
    marked_frag = input_fragments
    pinyin_list = pinyin(marked_frag, style=Style.TONE3, neutral_tone_with_five=True)
    extended = t.extend_marked_frag(marked_frag, mark)
    t.modify_bu_tone(pinyin_list, extended)
    assert pinyin_list == expected_pinyin


@pytest.mark.skipif(not t._HAS_JIEBA, reason="可选模块")
@pytest.mark.parametrize("input, expected", [
    ([], []),
    ([""], []),
    (["/0", "有一个人前来买瓜", "/0"], ["/0", "有", "一个", "人", "前来", "买瓜", "/0"]),
    (["/0", "只因/0你太美", "/0"], ["/0", "只", "因", "/", "0", "你", "太美", "/0"]),
])
def test_tokenize(input, expected):
    assert t.tokenize(input, None) == expected


@pytest.mark.parametrize("input", [
    [],
    [""],
    ["汉"],
    ["我不明白", "为什么大家都在谈论", "项羽被困垓下"],
])
def test_hanzi(input):
    t.hanzi_process(input, None, None)


@pytest.mark.parametrize("input", [
    ["測試unexpected的非漢字輸入", "比如々", "還有молоко"],
])
def test_hanzi_illegal(input):
    with pytest.raises(ValueError, match=r"处理结果出错：展开后的片段长度\(\d+\)与拼音列表长度\(\d+\)不相等！"):
        t.hanzi_process(input, None, None)