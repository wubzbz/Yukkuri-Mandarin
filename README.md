# Yukkuri-Mandarin: 油库里普通话

<!--[![PyPI - Version](https://img.shields.io/pypi/v/yukkuri-mandarin.svg)](https://test.pypi.org/project/yukkuri-mandarin)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/yukkuri-mandarin.svg)](https://test.pypi.org/project/yukkuri-mandarin)-->
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Type Checked](https://img.shields.io/badge/types-checked-green.svg)](https://mypy.readthedocs.io/)

<img width="1280" height="640" alt="欢迎来到油库里普通话！" src="https://github.com/user-attachments/assets/836f84ec-d0ba-4373-93e1-1318e44273dd" />

-----

油库里普通话（Yukkuri-Mandarin）是一个尝试使用日语的假名（五十音）系统来模拟拼读现代汉语普通话的Python包。

“伪中国语”（偽中国語 / ぎちゅうごくご）是一种基于日语逻辑，但不使用日语中的假名，仅通过汉字来构建句子的语言游戏形式。反过来，仅使用日语假名来拼读普通话发音形成的“句子”或可称之为“伪日本语”。例如“油库里普通话”，使用平假名模拟其**音节**将是“よう　くう　りい　ぷう　とん　ふわ”。同时，基于日语高低音模式模拟普通话**声调**，得到类似“ <ins>よ</ins>/̅う̅く̅\\<ins>うりいぷう</ins>/̅と̅ん̅ふ̅\\<ins>わ</ins>”的结果。

目前，现有的普通话->假名转换工具大部分仅能实现[音节](https://github.com/wubzbz/Yukkuri-Mandarin/blob/main/docs/phonology.md/#基本概念)的模拟，而不能还原[声调](https://github.com/wubzbz/Yukkuri-Mandarin/blob/main/docs/phonology.md/#基本概念)。如果直接利用其输出的结果生成[油库里语音](https://github.com/wubzbz/Yukkuri-Mandarin/blob/main/docs/phonology.md/#什么是油库里语音)将得到类似“棒读”的机械发音。本项目在实现这些功能的基础上，借助语音合成软件的“[音声记号](https://github.com/wubzbz/Yukkuri-Mandarin/blob/main/docs/phonology.md/#什么是音声记号)”，在输出结果中标记高低音形成声调拟音，使发音更加接近普通话。您可以将转换结果用于[AquesTalkPlayer](https://www.a-quest.com/products/aquestalkplayer.html)、[油库里MovieMaker](https://manjubox.net/ymm4/)和其他支持音声记号的语音合成工具，以实现中文油库里语音的合成。此外，本项目还提供了拼音数据库管理功能，如果您对某个字的发音不满意，或者某些生僻字缺少发音，您可以方便地自定义发音数据。祝您玩得愉快~

> 让我们说中文！


## 目录

- [安装方法](#安装方法)
- [使用方法](#使用方法)
- [环境与依赖](#环境与依赖)
- [常见问题](#常见问题)
- [更新日志](#更新日志)
- [许可证](#license)


## 安装方法

:star: **（推荐）** 安装所有可选依赖项：

```bash
pip install yukkuri-mandarin[jieba, openpyxl]
```

不带可选依赖项：

```bash
pip install yukkuri-mandarin
```

使用可选依赖项 `jieba` 进行分词可以提高多音字读音准确性：

```bash
pip install yukkuri-mandarin[jieba]
```

如果要使用导出/导入Excel文档的功能，请安装可选依赖项 `openpyxl` ：

```bash
pip install yukkuri-mandarin[openpyxl]
```

如果要从本地安装/给无法联网的设备安装/从源码编译安装，请看[更多安装方式](https://github.com/wubzbz/Yukkuri-Mandarin/blob/main/docs/installation.md)。


## 使用方法

1

请查看更详细的[使用方法介绍](https://github.com/wubzbz/Yukkuri-Mandarin/blob/main/docs/Contents.md)。


## 环境与依赖

- 支持 **Python 3.9** 及以上。

- 必需依赖：

    - [pypinyin](https://pypi.org/project/pypinyin/) 0.54.0 及以上。

- 可选依赖：

    - [jieba](https://pypi.org/project/jieba/) 0.42.1 及以上。
    
    - [openpyxl](https://pypi.org/project/openpyxl/) 3.1.5 及以上。

谨在此向上述包的开发者们表达感谢！ :smile:


## 常见问题

Q: 我需要有日语基础吗？

A: **不需要。** 但是如果您掌握了假名发音将帮助您调整您不满意的发音数据。

Q: 某个音读错了/缺少某个音/我想修改某个音

A: 请使用[拼音数据库管理](https://github.com/wubzbz/Yukkuri-Mandarin/blob/main/docs/database-mngr.md)模块。

Q：我遇到了问题/我有一个建议/我需要某个功能

A：请在[issue](https://github.com/wubzbz/Yukkuri-Mandarin/issues)板块提出，或者给作者发邮件：wubzbz@126.com


## 更新日志

### 0.6.0(Test Pypi)

2025/08/24

- 添加了拼音序列转换功能。
- 添加了去除音声记号选项。
- 添加了片假名转换平假名函数。
- 完成了单元测试。

查看更多[更新日志](https://github.com/wubzbz/Yukkuri-Mandarin/blob/main/docs/CHANGELOG.md)。


## 许可证

[`yukkurimandarin`](https://pypi.org/project/yukkuri-mandarin/) is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
