# AGENTS.md

面向 AI 编码代理的仓库指南。本文档描述本仓库（`Yukkuri-Mandarin/`，即 git 仓库根）的结构、常用命令、架构与编码规范，帮助代理高效、正确地开展工作。

---

## 1. 项目概述

**Yukkuri-Mandarin（油库里普通话）** 是一个使用日语假名（五十音）系统模拟拼读现代汉语普通话的 Python 包，发布在 PyPI（`yukkuri-mandarin`）。

- 核心功能：将中文句子或拼音序列转换为"伪日本语"（假名拟音），并借助语音合成软件的**音声记号**标记高低音、模拟普通话声调。
- 输出可供 AquesTalkPlayer、油库里MovieMaker4（YMM4）等支持音声记号的工具合成中文油库里语音。
- 附带拼音数据库管理功能：可自定义/增删改某个字（音节）的假名发音数据。
- 包名（PyPI）：`yukkuri-mandarin`；导入名：`yukkurimandarin`。
- 当前版本：1.0.3（版本号以 `pyproject.toml` 为准）。要求 Python >= 3.9, < 4。

## 2. 技术栈与依赖

- 构建/打包：Poetry（`poetry-core>=2.0.0,<3.0.0`），配置见 `pyproject.toml`。
- **必需依赖**：`pypinyin>=0.54.0`。
- **可选依赖**（以 `try/except` 方式引入，缺失时功能降级而非报错）：
  - `jieba>=0.42.1`：分词，提高多音字读音准确率。
  - `openpyxl>=3.1.5`：Excel（xlsx）导入导出。
  - 可选组安装：`pip install yukkuri-mandarin[all]` / `[jieba]` / `[openpyxl]`。
- 开发依赖：`pytest>=8.4.1`（`[tool.poetry.group.dev.dependencies]`）。
- `requirements.txt` 为固定版本的完整依赖清单（含测试依赖），供 CI 使用。

## 3. 常用命令

```bash
# 安装（开发模式，含可选与测试依赖）
pip install -e .[all]
# 或使用 Poetry
poetry install --all-extras

# 运行全部测试（pytest 配置在 pyproject.toml：[tool.pytest.ini_options]）
pytest

# 运行单个测试文件
pytest tests/test_core.py

# lint（与 CI 一致：语法错误/未定义名为硬性错误，其余为警告）
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

## 4. 仓库结构

```
Yukkuri-Mandarin/
├── pyproject.toml            # 项目元数据、依赖、pytest 配置
├── requirements.txt          # 固定版本依赖（CI 用）
├── README.md                 # 项目说明（简体中文）
├── LICENSE                   # MIT
├── .github/workflows/
│   ├── CI.yml                # PR 到 main：flake8 + pytest（3 OS × Python 3.9–3.13）
│   └── CD.yml                # PR 合并到 main：发布 PyPI 与 GitHub Release
├── docs/                     # 中文文档
│   ├── usage.md              # 使用方法
│   ├── installation.md       # 安装方法
│   ├── database-mngr.md      # 拼音数据库管理
│   ├── phonology.md          # 语音学原理（音节/声调/音声记号）
│   ├── CHANGELOG.md          # 更新日志（发版必须更新）
│   └── Asset/                # 图片素材
├── yukkurimandarin/          # 源码包（导入名）
│   ├── core.py               # 公共入口 text_convert / pinyin_convert
│   ├── pre_process.py        # 输入预处理
│   ├── digit_to_chinese.py   # 阿拉伯数字 → 汉字
│   ├── hanzi_process.py      # 汉字片段处理
│   ├── non_hanzi_process.py  # 非汉字片段处理
│   ├── post_process.py       # 输出后处理（去音声记号等）
│   ├── settings.py           # NonHanziModes 参数对象
│   ├── database.py           # Database：SQLite 基础类
│   ├── database_mngr.py      # DatabaseManager：数据库管理
│   ├── generate_gana.py      # 按全局规则生成假名（批量生成用）
│   ├── generate_table.py     # 生成音节表 fill_csv / fill_xlsx
│   ├── __init__.py           # 包级导出（__all__）
│   └── data/yinjie_database.db  # 内置拼音数据库（SQLite）
└── tests/
    ├── test_*.py             # 每个模块对应一个测试文件
    ├── test.py               # 临时手动运行脚本（勿作为正式测试）
    ├── modify_pydb.py        # 生成并更新数据库脚本
    └── test_data/            # 测试数据（*.csv / *.xlsx，被 .gitignore 忽略）
```

## 5. 架构与数据流

### 5.1 转换管线（`text_convert`）

```
输入句子 → pre_process（数字转汉字等）→ divide（切分汉字/非汉字片段）
        → hanzi_process / non_hanzi_process（分别处理）
        → combine（按片段顺序重组）→ post_process（去音声记号等）→ 输出
```

- `divide()`：按 `is_hanzi()` 将句子切成汉字片段与非汉字片段列表，并返回最后片段类型。
- `combine()`：依据片段数量关系（等长 / HNH / NHN）将两类结果交替重组回句子。
- `hanzi_process()`：使用 pypinyin 获取拼音，可选 jieba 分词消歧，再查询数据库得到假名拟音（含音声记号）。
- `non_hanzi_process()`：按 `NonHanziModes` 处理英文、日文、标点等非汉字内容（模式：`ignore` / `keep` / `replace` / 自定义可调用函数）。
- `post_process()`：统一收尾；`without_accent=True` 时去除音声记号。

### 5.2 拼音入口（`pinyin_convert`）

输入以空格分隔的拼音（音节末尾带声调数字 0–5，如 `you2 ku4 li3`），构造"前音+当前+后音"声调序列（如 `"121"`），直接查询数据库得到假名拟音；标点字符（`, . ; ?`）映射为全角标点。

### 5.3 数据库

- SQLite 表 `pinyin_data`：
  ```sql
  CREATE TABLE IF NOT EXISTS pinyin_data (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      yinjie TEXT NOT NULL,     -- 音节（拼音）
      tone TEXT NOT NULL,       -- 声调序列（如 "121"）
      hiragana TEXT NOT NULL,   -- 假名拟音（可含音声记号）
      UNIQUE (yinjie, tone) ON CONFLICT REPLACE
  )
  ```
- 默认库文件：`yukkurimandarin/data/yinjie_database.db`（`Database.DEFAULT_DB_PATH`）。
- `DatabaseManager` 提供增删改查、批量导入，默认在当前工作目录读写 `yinjie_table.xlsx` / `yinjie_table.csv`（表头：音节、声调、平假名）。
- `generate_table.py` / `generate_gana.py`：依据全局规则快速生成/重建音节表，用于批量构建数据库。

## 6. 编码规范

- **语言**：注释与文档字符串使用简体中文；标识符、代码与字符串字面量为英文。
- **类型注解**：全项目使用 `typing` 类型注解（`Optional`、`List`、`Tuple`、`Union`、`Callable` 等）。
- **文档字符串**：函数 docstring 采用 `Args:` / `Returns:` / `Usage:` 结构，`Usage:` 中含可直接运行的示例（doctest 风格）。
- **可选依赖**：一律用 `try/except ImportError` 包裹导入，并设置标志位（如 `_HAS_OPENPYXL`），供测试 `skipif` 使用；不要在模块顶层直接 import 可选包。
- **错误处理**：参数类型错误抛 `ValueError`，消息为中文（如 `f"参数sentence必须是字符串: {sentence}"`）。
- **风格约束**（CI flake8）：行宽 ≤ 127，复杂度 ≤ 10；`E9/F63/F7/F82` 为硬性错误。
- **导出**：新增公共 API 时同步更新 `yukkurimandarin/__init__.py` 的 `__all__`。
- **编码**：所有文件 UTF-8，无 BOM。

## 7. 测试规范

- 测试框架：pytest（配置见 `pyproject.toml` 的 `[tool.pytest.ini_options]`：`pythonpath = "yukkurimandarin"`，`testpaths = "tests"`，因此测试中直接 `import yukkurimandarin...` 即可）。
- 命名：`tests/test_<模块名>.py`，与源码模块一一对应。
- 风格：大量使用 `@pytest.mark.parametrize` 做表驱动测试；纯函数（如 `divide`、`combine`）断言输入输出对。
- 可选依赖相关的测试需用 `@pytest.mark.skipif(not t._HAS_OPENPYXL, reason="可选模块")` 跳过。
- 注意：`tests/test_data/` 下的 `*.csv` / `*.xlsx` 与仓库根的 `gr_yinjie_table.xlsx` 被 `.gitignore` 忽略，不会入库；测试本身会重新生成这些文件。运行测试后若产生新文件，属正常现象，不要提交。
- `tests/test.py` 与 `tests/modify_pydb.py` 是手动脚本（通过 `.vscode/launch.json` 的 debugpy 配置运行），不是正式测试。

## 8. 发版与 CI/CD

- **CI**（`CI.yml`）：PR 到 `main` 时触发（`docs/**` 与 `README.md` 变更不触发）；矩阵 3 个 OS × Python 3.9–3.13；跑 flake8 + pytest。push 不触发（避免重复）。
- **CD**（`CD.yml`）：PR 合并到 `main` 时自动发布。
  - 版本号取自 **PR 分支名**（如分支 `1.0.4` → 版本 `v1.0.4`），tag 为 `v<分支名>`。
  - 构建并发布到 PyPI（可信发布，`skip-existing: true`），并创建 GitHub Release（内容指向 CHANGELOG）。
- **发版清单**：
  1. 新建分支，分支名 = 新版本号（如 `1.0.4`）；
  2. 更新 `pyproject.toml` 的 `version`；
  3. 在 `docs/CHANGELOG.md` 顶部新增版本条目（含日期与改动列表），README 的更新日志一并同步；
  4. 开 PR 到 `main` 并合并 → CD 自动发布。

## 9. 注意事项与陷阱

- **不要提交** `*.csv`、`*.xlsx`、`*.old`（`.gitignore` 规则），包括测试生成的表文件。
- 修改发音规则 / 数据库内容时，注意 `generate_gana.py` 与 `generate_table.py` 的联动：先改规则，再运行 `tests/modify_pydb.py` 重建数据库。
- 音声记号（如 `/`、`\`、`'`）是功能的一部分，单元测试断言结果时需保留它们；`without_accent` 参数负责去除。
- 若在 Windows 控制台看到中文乱码，是控制台代码页（GBK）问题，文件本身是 UTF-8，不要"修复"文件编码。
