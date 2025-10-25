# 用于修改拼音数据库

import yukkurimandarin as ym

dm = ym.DatabaseManager()

dm.search_by_pinyin("zi", "*5*")