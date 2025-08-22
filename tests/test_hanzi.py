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
    ["測試unexpected的非漢字輸入", "比如枠", "還有молоко"],
])
def test_hanzi(input):
    t.hanzi_process(input, None)