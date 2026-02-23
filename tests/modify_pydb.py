# 用于修改拼音数据库

import yukkurimandarin as ym

ym.fill_xlsx()

dm = ym.DatabaseManager()

dm.import_from_excel("gr_yinjie_table.xlsx")