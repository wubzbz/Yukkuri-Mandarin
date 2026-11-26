# AGENTS.md

面向 AI 编码代理的仓库指南。本文档描述本仓库（`Yukkuri-Mandarin/`，即 git 仓库根）的结构、常用命令、架构与编码规范，帮助代理高效、正确地开展工作。

> 本文档对应 **2.0**。1.0 的 `core.py`、`database.py`、`database_mngr.py`、`generate_gana.py`、`generate_table.py` 等模块已经删除；如果看到旧文档或旧代码片段，以本文档和 `yukkurimandarin/` 下的实际代码为准。

---

## 1. 项目概述

**Yukkuri-Mandarin（油库里普通话）** 是一个使用日语假名（五十音）模拟拼读现代汉语普通话的 Python 包，发布在 PyPI（`yukkuri-mandarin`）。

- 核心功能：将中文句子或拼音序列转换成"伪日本语"（假名拟音），并用音声记号（`/`、`'`、`_`）标记高低音、模拟普通话声调。
- 输出可供 AquesTalkPlayer、油库里MovieMaker4（YMM4）等支持音声记号的工具合成中文油库里语音。
- 附带拼音数据库管理：内置只读库 + 用户自维护的可写库，支持 CSV / XLSX 导入导出与按规则重建。
- 包名（PyPI）：`yukkuri-mandarin`；导入名：`yukkurimandarin`。
- 当前版本：**2.0.0**（以 `pyproject.toml` 为准）。要求 Python `>=3.9,<4`。

## 2. 技术栈与依赖

- 构建/打包：uv（`uv_build` 构建后端），配置见 `pyproject.toml`；依赖锁定用 `uv.lock`。
- **必需依赖**：`pypinyin>=0.54.0`。
- **可选依赖**（在函数内部懒加载，缺失时降级或抛 `MissingDependencyError`，不要在模块顶层直接 import）：
  - `jieba>=0.42.1`：分词，仅用于多音字消歧。
  - `openpyxl>=3.1.5`：Excel（xlsx）导入导出。
  - 安装：`pip install yukkuri-mandarin[all]` / `[jieba]` / `[openpyxl]`。
- 开发依赖：`pytest>=8.4.1`、`flake8>=7.0.0`（`[dependency-groups] dev`）。
- `uv.lock` 是唯一的依赖锁定文件；不再维护 `requirements.txt` / `poetry.lock`。

## 3. 常用命令

```bash
# 同步开发环境（含可选与测试依赖）
uv sync --all-extras

# 运行全部测试
uv run pytest

# 运行单个测试文件
uv run pytest tests/test_sandhi.py

# lint（与 CI 一致）
uv run flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
uv run flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# 构建发行文件（生成到 dist/）
uv build

# 按规则重建数据库（输出到指定路径；默认 yinjie_database.db）
uv run python -m yukkurimandarin.tools.build_db out.db --overwrite
```

本地 `uv run` 会在仓库根使用 `.venv/`；`.flake8` 已排除 `.venv`、`dist`、`build`、`yukkurimandarin-bak`。

## 4. 仓库结构

```text
Yukkuri-Mandarin/
├── pyproject.toml            # 项目元数据、依赖、uv_build、pytest 配置
├── uv.lock                   # 依赖锁定（uv 生成）
├── .flake8                   # flake8 配置（排除 .venv、dist、backup 等）
├── README.md                 # 项目说明（简体中文）
├── LICENSE                   # MIT
├── AGENTS.md                 # 本文件
├── .github/workflows/
│   ├── CI.yml                # PR 到 main：flake8 + pytest（3 OS × Python 3.9–3.13）
│   └── CD.yml                # PR 合并到 main：发布 PyPI 与 GitHub Release
├── docs/                     # 中文文档
│   ├── usage.md              # 使用方法
│   ├── installation.md       # 安装方法
│   ├── database-mngr.md      # 拼音数据库管理
│   ├── phonology.md          # 语音学原理
│   ├── CHANGELOG.md          # 更新日志（发版必须更新）
│   └── Asset/                # 图片素材
├── yukkurimandarin/          # 源码包（导入名）
│   ├── __init__.py           # 公共导出与 __version__
│   ├── api.py                # 公共入口：Converter / text_convert / pinyin_convert
│   ├── chars.py              # 字符分类、汉字/数字判断、假名归一化
│   ├── segments.py           # Document / Run / Syllable 数据模型与不变量
│   ├── settings.py           # Config / NonHanziModes（frozen dataclass）
│   ├── errors.py             # MissingDependencyError
│   ├── formats.py            # 表格列名（CSV_HEADERS）
│   ├── data/yinjie_database.db  # 内置拼音数据库（SQLite，只读）
│   ├── db/                   # SQLite 层
│   │   ├── connection.py     # 打开连接、只读判定、版本检查/迁移
│   │   ├── schema.py         # schema v1、v0→v1 迁移与恢复
│   │   ├── repository.py     # PinyinRepository：增删查改、批量、分块
│   │   ├── models.py         # PinyinEntry
│   │   ├── transfer.py       # CSV / XLSX 读写
│   │   ├── report.py         # 对齐表格输出
│   │   └── errors.py         # YukkuriDBError 及子类
│   ├── phonology/            # 纯语音学规则（不碰数据库）
│   │   ├── pinyin.py         # pypinyin 包装、serial 构造
│   │   └── sandhi.py         # 上声 / 不 / 一 的变调
│   ├── pipeline/             # 转换管线
│   │   ├── normalize.py      # 数字转汉字、输入归一化
│   │   ├── hanzi.py          # fill_pinyin / fill_kana
│   │   ├── non_hanzi.py      # 非汉字片段处理
│   │   ├── assemble.py       # 按片段拼装 + 去音声记号
│   │   └── post.py           # finalize（整串收尾，pinyin_convert 用）
│   ├── tablegen/             # 音节表生成
│   │   ├── render.py         # 415 个音节、声调 → 假名/音声记号
│   │   └── table.py          # valid_tones、fill_csv / fill_xlsx
│   └── tools/
│       └── build_db.py       # 按规则重建数据库（CLI）
└── tests/
    ├── test_*.py             # 与模块对应的测试（16 个文件）
    ├── test.py               # 手动计时脚本（勿作为正式测试）
    ├── modify_pydb.py        # 手动重建数据库脚本
    └── test_data/            # 测试数据（*.csv / *.xlsx，被 .gitignore 忽略）
```

## 5. 架构与数据流

### 5.1 公共 API

```python
from yukkurimandarin import (
    Config, Converter, DEFAULT_CONFIG, NonHanziModes,
    PinyinEntry, PinyinRepository,
    text_convert, pinyin_convert, fill_csv, fill_xlsx,
)

text_convert("你好")                      # 便捷入口，每次新建 Converter
text_convert("你好", without_accent=True)
pinyin_convert("ni3 hao3", error="")

with Converter(Config(database="mine.db")) as conv:
    conv.text_convert("你好")             # 复用连接与分词器
```

- `text_convert(sentence, *, without_accent=False, config=DEFAULT_CONFIG, tokenizer=None)`：单次转换。
- `pinyin_convert(sentence, *, error="", without_accent=False, config=DEFAULT_CONFIG)`：拼音序列转换。
- `Converter(config=DEFAULT_CONFIG, tokenizer=None)`：持有懒加载的数据库连接与分词器，是上下文管理器；批量调用时复用。
- 顶层 `text_convert` / `pinyin_convert` 每次调用会新建 `Converter`（随之打开一次数据库）；默认 jieba 分词器是进程内单例。批量转换仍建议复用 `Converter`。
- `Config` 是 frozen dataclass：`non_hanzi: Optional[NonHanziModes]`、`database: Optional[Union[str, Path]]`；用 `dataclasses.replace(DEFAULT_CONFIG, ...)` 派生。
- `NonHanziModes` 的 `global_mode` 可取 `"ignore"` / `"keep"` / `"replace"` / 可调用对象；细分类别（en/ja/pc/other）未指定时回落到全局值。

### 5.2 文本转换管线（`text_convert`）

```text
输入句子
  → normalize_text（阿拉伯数字转汉字、输入归一化）
  → Document.from_text（按字符类别切成 run，并为汉字建立 Syllable 轨道）
  → fill_pinyin（pypinyin TONE3 + neutral_tone_with_five；jieba 仅用于分词消歧）
  → sandhi.apply（连读上声 → 不 → 一）
  → fill_kana（用前/本/后三字声调构造 serial，查数据库取假名）
  → assemble（非汉字按 NonHanziModes 处理；汉字段收尾）
  → 输出
```

- 没有汉字段时，管线跳过 jieba 和数据库，只处理非汉字。
- `Document` 由若干 `Run(kind, start, end, syl_start, syl_end)` 和全局对齐的 `Syllable(char, syllable, tone, kana)` 组成；`kind` 为 `"hanzi"` / `"gana"` / `"latin"` / `"punctuation"` / `"others"`。
- run 必须连续覆盖全文，非汉字段的 `syl_start == syl_end`，汉字段长度等于音节数；这些不变量在构造时校验。
- 变调只在汉字 run 内部生效，run 边界视为停顿（替代 1.0 的 `/0` 哨兵）。
- `without_accent=True` 只作用于**生成的汉字段**；`keep` 模式保留下来的原文（如 `a_b`、片假名）不会被改写。

### 5.3 拼音入口（`pinyin_convert`）

- 输入以空白分隔，音节末尾带声调数字；`0` 视作轻声 5（如 `ma0` 等价于 `ma5`）。
- 用前/本/后三字声调构造三位 serial（如 `"121"`），查询数据库得到假名。
- 标点 `, . ; ?` 按固定表映射（旧行为）。
- `error` 是查不到时的返回值；传 `"keep"` 时保留原音节。

### 5.4 变调规则（`phonology/sandhi.py`）

- 顺序：`apply_third_tone` → `apply_bu` → `apply_yi`；`apply()` 只应对**原始拼音**调用一次，重复调用会叠加“不”的变调。
- 上声：连续上声按旧的机械 2+1 分组（`[3,3] → [2,3]`，`[3,3,3] → [2,2,3]`）。
- “不”：轻声（5）保持；“不+不”保持；否则后字为 4 时读 2，其余读 4。
- “一”：数字语境按位数规则；`V-一-V` 中读轻声（用数词/量词表排除“一步一步”“一年一年”“一百一百”这类非动词重叠）；其余按“后字 4 → 2，否则 4”。
- 已知限制见第 10 节。

### 5.5 数据库

- schema v1：

  ```sql
  CREATE TABLE IF NOT EXISTS pinyin_data (
      yinjie   TEXT NOT NULL,
      tone     TEXT NOT NULL CHECK (length(tone) = 3),
      hiragana TEXT NOT NULL,
      PRIMARY KEY (yinjie, tone)
  ) WITHOUT ROWID;
  ```

  通过 `PRAGMA user_version = 1` 标记版本；没有 `id` 列。
- 内置库：`yukkurimandarin/data/yinjie_database.db`，74,700 条（415 音节 × 180 声调模式）。
- **内置库是严格的只读资源**：
  - `PinyinRepository.open(None)` 或打开内置路径时强制只读（含硬链接，用 `os.path.samefile` 判断）。
  - `PinyinRepository.create()` 拒绝把内置路径作为输出。
  - 升级/重建内置库必须先生成到临时路径，再手工替换。
- 用户库：`PinyinRepository.open(path)` 可写；`Config(database=...)` 的转换路径默认**只读**打开，若 schema 落后则迁移一次后继续只读。
- `create()` 先校验全部记录，再写同目录临时文件，成功后 `os.replace` 原子替换；失败不破坏旧库。
- 迁移在 `SAVEPOINT` 中执行，失败回滚；能恢复上次中断留下的 `pinyin_data_v0`。
- 不强制 WAL；`create()` 产出的库是默认 `delete` 日志模式，只读打开不会产生 `-wal`/`-shm`。
- 异常：`YukkuriDBError` 为基类；`SchemaError`、`ReadOnlyDatabaseError`、`DatabaseUnavailableError`、`TransferError`。sqlite3 原生异常在仓储/连接边界被包装为 `DatabaseUnavailableError`。

### 5.6 音节表与重建

- `tablegen.render.syllables()` 返回 415 个音节；`valid_tones()` 返回 180 个三位模式（首位 0–5、中位 1–5、末位 0–5，中位不能为 0）。
- `render_hiragana(yinjie, tone, without_accent=False)` 按规则生成假名与音声记号。
- `fill_csv(path=None)` / `fill_xlsx(path=None)` 写出全表；默认 `gr_yinjie_table.csv` / `.xlsx`，后缀不对会自动修正。
- `tools.build_db`：`python -m yukkurimandarin.tools.build_db [output] [--overwrite]`，按规则生成 74,700 条记录；拒绝内置路径，失败返回码 1。

## 6. 编码规范

- **语言**：注释与文档字符串使用简体中文；标识符、代码与字符串字面量为英文。
- **类型注解**：全项目使用类型注解；需要前向引用时用 `from __future__ import annotations`。
- **文档字符串**：函数 docstring 采用 `Args:` / `Returns:` / `Raises:`（必要时 `Usage:`）结构。
- **不可变配置**：`Config` / `NonHanziModes` 是 frozen dataclass，不要在运行时改全局配置；需要变体用 `dataclasses.replace`。
- **可选依赖**：在函数内部 `try/except ImportError` 懒加载；缺失时抛 `MissingDependencyError` 或降级，不要在模块顶层直接 import。
- **错误处理**：参数错误抛 `ValueError`，消息为中文；数据库异常使用 `db/errors.py` 中的类型；不要把 sqlite3 原生异常直接暴露给调用方。
- **数据模型**：新增/修改 `Document` 时保持 run 连续、音节对齐等不变量，并在 `segments._validate*` 中校验。
- **风格约束**（CI flake8）：行宽 ≤ 127，复杂度 ≤ 10；`E9/F63/F7/F82` 为硬性错误。
- **导出**：新增公共 API 时同步更新 `yukkurimandarin/__init__.py` 的 `__all__`。
- **编码**：所有文件 UTF-8，无 BOM。

## 7. 测试规范

- 框架：pytest；配置在 `pyproject.toml` 的 `[tool.pytest.ini_options]`（`pythonpath = "."`、`testpaths = "tests"`）。
- 当前基线：`uv run pytest` → **465 passed**；`uv run flake8 . --max-complexity=10 --max-line-length=127` → 0。
- 命名：`tests/test_<模块名>.py`，与源码模块对应；大量使用 `@pytest.mark.parametrize` 做表驱动测试。
- 文件系统：使用 `tmp_path`，不要写仓库内文件；不要引入 session 级 fixture。
- 内置库：测试默认转换会读内置库；不要尝试写它。需要可写库时用 `PinyinRepository.create(tmp_path / "x.db", ...)`。
- 可选依赖：用 `pytest.importorskip("jieba")` / `pytest.importorskip("openpyxl")`，不要用模块级 `_HAS_*` 标志。
- `tests/test.py`、`tests/modify_pydb.py` 是手动脚本，不会被 pytest 收集。
- 修改数字读法、变调或数据库行为时，务必补对应的参数化用例。

## 8. 发版与 CI/CD

- **CI**（`CI.yml`）：PR 到 `main` 时触发（`docs/**`、`README.md` 变更不触发）；矩阵 3 OS × Python 3.9–3.13；`uv sync --frozen --all-extras` 后跑 flake8（硬错误 + 警告）与 pytest。
- **CD**（`CD.yml`）：PR 合并到 `main` 时触发；`uv build` 后发布 PyPI（可信发布，`skip-existing: true`），并创建 GitHub Release。
- CD 用 **PR 分支名**作为版本号（tag `v<分支名>`）。发布分支请直接以版本号命名（如 `2.0.0`），不要用 `dev/2.0.0-alpha` 这类带 `/` 的名字，否则 tag 不合法。
- **发版清单**：
  1. 新建分支，分支名 = 新版本号；
  2. 更新 `pyproject.toml` 的 `version`；
  3. 在 `docs/CHANGELOG.md` 顶部新增版本条目（日期 + 改动列表），必要时同步 README；
  4. 开 PR 到 `main` 并合并 → CD 自动发布。

## 9. 注意事项与陷阱

- **不要直接写内置库**。需要重建时先 `build_database` 到临时路径，再复制替换 `yukkurimandarin/data/yinjie_database.db`；复制后确认 `PRAGMA journal_mode` 为 `delete`、目录下没有 `-wal`/`-shm`。
- 修改发音规则时，规则在 `tablegen/render.py`，重建数据库用 `tools/build_db.py`；不要手改 SQLite 行。
- `apply()` 只能对原始拼音调用一次；不要把变调后的 Document 再传进去。
- `without_accent` 只清理生成部分；不要用它来清洗用户原文。
- 数字读法按“亿 / 万 / 个”分级；改 `normalize.py` 时跑 `test_normalize.py` 的全部分级用例。
- 不要提交 `*.csv`、`*.xlsx`、`*.old`、`*.db-wal`、`*.db-shm`，以及根目录导出的 `/yinjie_database.db`（已在 `.gitignore`）。
- Windows 控制台中文/假名乱码是代码页（GBK）问题，文件本身是 UTF-8，不要“修复”文件编码。
- `yukkurimandarin-bak/` 是 1.0 备份，已被 git 忽略，也被 `.flake8` 排除；不要从里面 import。
- 1.0 的 `core.divide/combine`、`/0` 哨兵、`DatabaseManager` 都已删除；迁移旧代码时改用 `Document`、`PinyinRepository`。

## 10. 已知限制

- 连续上声使用机械 2+1 分组：`我很好` 会得到 `2+2+3`，而非正确的 `1+2`。
- `一楼` 这类序数/数量歧义无法只靠字面判断，默认按数量词读去声。
- `V-一-V` 用数词/量词表做启发式排除；名词重叠等边缘情况仍可能误判。
- `动词 + 一 + 量词`（看一眼、等一下）未读轻声，只处理了 `V-一-V`。
- jieba 只参与多音字消歧，不参与上声变调分组。
- 汉字识别范围是基本区 `U+4E00–U+9FFF`，扩展 A 区暂不识别。
- 音声记号的生成规则与 1.0 保持一致，未做声学优化。
