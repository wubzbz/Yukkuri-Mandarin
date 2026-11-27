# 如何管理拼音数据库

> [!NOTE]
> 本文档适用于 **2.0** 版以上。旧版文档见 [archive/1.0/database-mngr.md](archive/1.0/database-mngr.md)。

## 0. 开始之前

本包内置了一个默认数据库，它是基于一定的[规则](https://github.com/wubzbz/Yukkuri-Mandarin/blob/main/docs/phonology.md)和作者的喜好制定的。**内置库只能读取，不能修改。**（允许用户直接修改包的内容通常不是一个好做法）

因此，如果您发现内置数据库有**错误**，请提交 Issue，我们一起看看是不是这样。如果您只是对我的方案不满意，想改发音，完全可以建立属于您的自定义数据库。

**一行数据**（有时我们也说“一条记录”, Entry）指的是**一个字在一种上下文里的读法。** 同一个字在不同词里可能对应多行数据（后面会详细解释）。

下面，我们就按“改一个字的发音”这个最常见的需求，一步一步演示。

## 1. 一行数据长什么样

数据库里每一行有三个字段：

| 字段 | 含义 | 例子 |
|---|---|---|
| 拼音 | 这个字的拼音，不带声调 | `shang` |
| 声调 | 三个数字，表示前、本、后的声调 | `043` |
| 假名 | 这个字要念成的假名（可以带音声记号） | `さ'あん` |

### 声调为什么是三个数字

因为一个字的假名写法与它前一个和后一个字的声调有关（详见[声调的处理](https://github.com/wubzbz/Yukkuri-Mandarin/blob/main/docs/phonology.md#4-声调的处理)）：

```text
声调 = 前一个字的声调 + 当前字的声调 + 后一个字的声调
          0～5            1～5          0～5
```

- `0` 表示“这边没有字”（比如句首、句尾）。
- `1`～`5` 分别是一声、二声、三声、四声、轻声。

以“上海”为例：

| 字 | 拼音 | 前 | 本 | 后 | 声调 |
|---|---|---|---|---|---|
| 上 | shang | 0（句首） | 4 | 3 | `043` |
| 海 | hai | 4 | 3 | 0（句尾） | `430` |

而“上海人”里的“海”字后面多了一个“人”（二声），所以它对应另一行数据：

| 字 | 拼音 | 前 | 本 | 后 | 声调 |
|---|---|---|---|---|---|
| 海 | hai | 4 | 3 | 2 | `432` |

所以，**同一个字在不同上下文里，可能对应不同的行**。改之前先确认您想改的是哪种情况。

> [!NOTE]
> 声调填的是**实际读出来的调**。比如“你好”的“你”会变调读成 ní，所以给这里的“你”字用的声调不是 `033`，而是 `023`。不确定时，可以先按下一节的方法 `get` 出来看看。

## 2. 改一个字的发音

### 第一步：复制内置库

新建一个 Python 文件（例如 `change.py`），保存下面的代码并运行：

```python
import shutil
from pathlib import Path
import yukkurimandarin

source = Path(yukkurimandarin.__file__).parent / "data" / "yinjie_database.db"
shutil.copy(source, "my_database.db")
print("已复制到 my_database.db")
```

现在当前目录下多了一个 `my_database.db`，它是可写的。

### 第二步：确认要改哪一行

先查一下原来的值。假设您想改“上海”的“上”：

```python
from yukkurimandarin import PinyinRepository

with PinyinRepository.open("my_database.db") as repo:
    print(repo.get("shang", "043"))
```

应该能看到类似：

```text
PinyinEntry(yinjie='shang', tone='043', hiragana="さ'あん")
```

如果打印的是 `None`，说明没有找到对应条目，可能拼音或声调写错了。

也可以一次性列出这个拼音的所有行，再挑出您需要的。只需省略声调参数：

```python
with PinyinRepository.open("my_database.db") as repo:
    for entry in repo.search("shang"):
        print(entry.tone, entry.hiragana)
```

### 第三步：修改假名

```python
from yukkurimandarin import PinyinEntry, PinyinRepository

with PinyinRepository.open("my_database.db") as repo:
    repo.upsert(PinyinEntry("shang", "043", "しゃ'ん"))
```

`upsert` 的意思是“有这一行就改，没有就加”。上面的例子把“上”在“上海”里的假名改成了 `しゃ'ん`。

> [!TIP]
> 这个单引号 `'` 是“音声记号”。音声记号的写法见[发音规则](https://github.com/wubzbz/Yukkuri-Mandarin/blob/main/docs/phonology.md#3-什么是音声记号)。

### 第四步：使用新数据库

```python
from yukkurimandarin import Config, text_convert

# 先在配置中指定数据库路径：
config = Config(database="my_database.db")

print(text_convert("上海", config=config))
```

输出应该变成了：

```text
しゃ'んはい
```

大功告成！

> [!TIP]
> “改了以后没生效”很可能是因为您忘了设置 `config` 的数据库路径，导致 `text_convert` 还是会用默认的内置库。

## 3. 批量修改（用表格）

只改一两个字时，用上一节的方法最省事。但假如要改很多字，可以把整份数据导出成表格，用 Excel 或文本编辑器改完再导回去。

### 导出

```python
from yukkurimandarin import PinyinRepository
from yukkurimandarin.db import write_table

with PinyinRepository.open() as repo:   # 不传路径 = 内置库，只读
    write_table(repo.iter_all(), "all.csv")
```

这会生成一个 `all.csv`，里面是内置库的全部数据。

> [!NOTE]
> 假如您安装了可选依赖 `openpyxl`，您可以导出为 `.xlsx` 文档，然后在 Excel 中处理。

### 修改

用表格软件打开 `all.csv`，只改您想改的那几行，保存时保持表头不变。

表头必须是：

```text
拼音,声调,平假名
```

### 用改好的表格新建数据库

```python
from yukkurimandarin import PinyinRepository
from yukkurimandarin.db import read_table

entries = read_table("all.csv")
PinyinRepository.create("my_database.db", entries, overwrite=True)
```

`overwrite=True` 表示如果 `my_database.db` 已存在就覆盖它。如果担心误修改已存在的文件，请将其设置为 `False`。

> [!NOTE]
> 假如您安装了可选依赖 `openpyxl`，您可以从 `.xlsx` 文档中读取数据。

### 只把改动的几行合并进现有库

如果您不想每次导整张表，也可以只准备改动过的行：

```python
from yukkurimandarin import PinyinRepository
from yukkurimandarin.db import read_table

with PinyinRepository.open("my_database.db") as repo:
    repo.upsert_many(read_table("my_changes.csv"))
```

`my_changes.csv` 只需要包含改过的行，表头同样要写全。

> [!NOTE]
> 导入表格时会逐行检查。只要有一行的格式不对（比如声调不是三位、声调中间是 0），就会报错并告诉您是第几行；改好那一行再重新导入即可。

## 4. 查询和删除

```python
from yukkurimandarin import PinyinRepository

with PinyinRepository.open("my_database.db") as repo:
    # 精确查一行
    entry = repo.get("hang", "220")
    print(entry)

    # 查某个拼音的所有行（可以用 * 通配声调）
    for entry in repo.search("hang", "2*0"):
        print(entry.tone, entry.hiragana)

    # 删除一行 / 删除一个拼音的所有行
    repo.delete("hang", "220")
    repo.delete_by_yinjie("hang")
```

声调中的 `*` 表示“这一位任意”，比如 `"2*0"` 只匹配第一位是 2、第三位是 0 的声调。

## 5. 常见问题

**改了没生效？**

- 最常见的原因：调用 `text_convert` 时忘了传 `config=Config(database="my_database.db")`。
- 拼音或声调和 `get` 出来的不完全一致，`upsert` 就变成了新增一行，而不是修改原来的行。
- 文件路径不对，改的是另一份 `.db`。

**只改了自定义库，其他字没了？**

如果您是从空库开始的，那库里只有您加的那几行，其他字自然查不到。请用第 2 节“复制内置库”的方法，或者第 3 节导入完整表格。

**报“只读数据库”/ `ReadOnlyDatabaseError`？**

内置库不能写。请复制一份再改；`PinyinRepository.open("内置库路径")` 会强制只读。

**报“声调格式错误”？**

声调必须是三个数字：前、本、后；每一位只能是 0～5，并且**第二位不能是 0**。

**导入表格报错？**

看报错里的行号，检查那一行：
- 表头是不是 `拼音,声调,平假名`（也接受 `音节`）；
- 三列是不是都有（假名可以为空）；
- 声调是不是三位、第二位不是 0。

**用 xlsx 时提示缺少 `openpyxl`？**

安装可选依赖：

```bash
pip install yukuri-mandarin[openpyxl]
```

只改 CSV 的话不需要它。

**旧版的 `DatabaseManager` 呢？**

2.0 已经移除。按本文的 `PinyinRepository` 用法即可；需要看旧写法时可以查阅[1.0 文档](archive/1.0/database-mngr.md)。

## 6. 进阶用法

- `repo.replace_all(entries)`：用一份完整表格**替换**整个库；表格里删掉的行也会从数据库删除。只想合并修改时用 `upsert_many`。
- `yukkurimandarin.fill_csv("template.csv")` / `yukkurimandarin.fill_xlsx("template.xlsx")`：按当前发音规则生成一份完整表格（74,700 行），可以用来查看格式或对比。
- `build_database(...)`（`from yukkurimandarin.tools.build_db import build_database`）：按规则重建整个数据库，属于开发/维护工具，普通改发音不需要用到。
