# 用于按规则重建拼音数据库（输出到当前目录）
#
# 注意：内置数据库是只读资源，本脚本不会直接覆盖它；
# 生成后如需替换内置库，请自行复制到 yukkurimandarin/data/ 下。

from yukkurimandarin.tools.build_db import build_database

build_database("yinjie_database.db", overwrite=True)
