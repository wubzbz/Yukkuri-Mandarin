# 更新日志

## 2.0.0

2026/11/26

> [!NOTE]
> 1.0版用户敬请查看：[迁移指南]()。

- ⚠️ 包结构重组为 `api` / `chars` / `segments` / `settings` / `db` / `phonology` /
  `pipeline` / `tablegen` / `tools`；1.0 的 `core`、`*_process`、
  `database` / `database_mngr`、`generate_*` 等模块全部移除。
- ⚠️ 公共 API 改为 `Config` + `Converter`：配置不可变，数据库路径收进 `Config`；
  `Converter` 懒加载并复用连接与分词器，顶层 `text_convert` / `pinyin_convert`
  改为关键字参数。
- ⚠️ 数据库层改为 `PinyinRepository`：schema v1（`(yinjie, tone)` 复合主键、
  去掉 id、WITHOUT ROWID），内置库强制只读，旧库自动迁移。
- 数据库写入更安全：`create()` 先校验全部记录，再写同目录临时文件并原子
  替换；v0→v1 迁移使用 SAVEPOINT，失败回滚，并能恢复中断迁移；不再强制 WAL。
- 转换路径默认以只读方式打开自定义库，schema 落后时迁移一次；输入中没有
  汉字段时不再加载 jieba 与数据库。
- 新增表格导入导出（`read_table` / `write_table`、`fill_csv` / `fill_xlsx`）
  与 `tools.build_db` 重建工具；内置库共 74,700 条（415 音节 × 180 声调模式）。
- 完善“一”的变调：去声前阳平，阴平/阳平/上声前去声；重叠动词中间读轻声，
  并排除“一步一步”“一年一年”“一百一百”等数词/量词重叠；多位数与数字串
  按惯例处理。
- 按“亿 / 万 / 个”分级重写整数读法，修正跨级零：
  `900005000` → `九亿零五千`，`100500000` → `一亿零五十万`。
- `pinyin_convert` 输入中的 `0` 视作轻声 5；`error="keep"` 保留原音节。
- `without_accent` 只清理生成的汉字段，`keep` 模式保留的原文不再被改写。
- 默认 jieba 分词器改为进程内单例并抑制 INFO 日志，重复调用不再重复加载
  词典；补充 `DatabaseUnavailableError` 等数据库异常层级，sqlite3 原生异常
  统一包装后抛出。
- 测试覆盖扩展到 465 项，`flake8` 0；CI 覆盖 Python 3.9–3.13。

## 1.0.4-alpha

2026/11/26

> 这是一个不公开发布的测试版本。

- 构建与依赖管理由 Poetry 迁移到 uv：改用 `uv_build` 构建后端，依赖锁定文件改为 `uv.lock`。
- 移除 `requirements.txt` 与 `poetry.lock`；开发依赖改由 `[dependency-groups] dev` 管理。
- CI/CD 改用 `astral-sh/setup-uv`，依赖安装用 `uv sync --frozen`，发布构建用 `uv build`。
- 新增 `.flake8` 配置，排除 `.venv`、`dist`、`build` 等目录。

## 1.0.3

2026/04/10

- 优化了对“不”字变调的支持。例如：“不对” -> "bu2 dui4"。
- 订正了油库里语音的介绍。
- 增加了面向ゆっくも！的使用说明。
- 修复了`modify_consecutive_threes()`潜在的数组越界漏洞。
- CI工作流不再在push时触发（避免重复）。

## 1.0.2

2026/02/23

- 优化（？）了部分发音。
    - 对于一些音节，缩短了其对应假名的拍数。例如-uo：`うお` -> `を`。
    - 将一些拍数较多的假名升/降调的时机后移。例如dian：`でぃ/あん` -> `でぃあ/ん`。
    - 参见[commit](https://github.com/wubzbz/Yukkuri-Mandarin/commit/a7f034ac8329d2ed789cc1d892661917a1478d6a)中对generate_gana.py的修改。
- 优化了jieba分词器初始化逻辑，抑制INFO级日志输出。
- 更新了许可证。

## 1.0.1

2025/10/21

- 修正了CI/CD忽略触发的范围。
- 改正了一些错别字。

## 1.0.0

2025/09/12

- 将CD工作流迁移到PyPI。

## 0.6.2(Test Pypi)

2025/09/12

- 完善文档。
- 将拼音数据库管理类的所有路径参数类型由`pathlib.Path`改为`str`。
- 修正了可选依赖包在toml文件中的设置。
- 清理了__pycache__文件夹。

## 0.6.1(Test Pypi)

2025/08/30

- 修复了在core.py直接引入`jieba`的问题。
- 将感叹号设置为full_stop。
- 将拼音数据库管理类的初始化路径参数类型由`pathlib.Path`改为`str`。
- 非汉字处理模式变量名现在符合BCP 47语言代码。

## 0.6.0(Test Pypi)

2025/08/24

- 添加了拼音序列转换功能。
- 添加了去除音声记号选项。
- 添加了片假名转换平假名函数。
- 完成了单元测试。

## 0.5.4(Test Pypi)

2025/08/23

- 修复了CD无法发布release的问题。
- 完成了单元测试。

## 0.5.3(Test Pypi)

2025/08/22

- 定义了CI/CD工作流。

## 0.5.2(Test Pypi)

2025/08/21

- 使用了参数对象管理非汉字处理模式。
- 测试了数据库模块。
- 实现了数据库操作结果格式化输出。

## 0.5.1

2025/07/30

- jieba分词函数从cut()改为使用lcut()返回列表。

## 0.5.0 

2025/07/29

- 修复了一些已知问题。

## 0.1 ~ 0.4

2025/07/29 以前

- 写了很多代码。
