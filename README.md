# Yukkuri-Mandarin: 油库里普通话

<!--[![PyPI - Version](https://img.shields.io/pypi/v/yukkurimandarin.svg)](https://pypi.org/project/yukkurimandarin)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/yukkurimandarin.svg)](https://pypi.org/project/yukkurimandarin)-->

题图。

-----

简介

## 目录

- [安装](#安装)
- [License](#license)

## 安装方法

### 简单安装：

不带可选依赖项：

```console
pip install yukkuri-mandarin
```

**（推荐）** 安装所有可选依赖项：

```console
pip install yukkuri-mandarin[jieba, openpyxl]
```

使用可选依赖项 `jieba` 进行分词可以提高多音字读音准确性：

```console
pip install yukkuri-mandarin[jieba]
```

如果要使用导出/导入Excel文档的功能，请安装可选依赖项 `openpyxl` ：

```console
pip install yukkuri-mandarin[openpyxl]
```

如果要从本地安装/给无法联网的设备安装/从源码编译安装，请看[更多安装方式]()。



## 使用方法

1

更详细的[使用方法介绍](/docs/Contents.md)。

## 环境与依赖

- 支持 **Python 3.9** 及以上。

- 必需依赖：

    - [pypinyin](https://pypi.org/project/pypinyin/) 0.54.0 及以上。

- 可选依赖：

    - [jieba](https://pypi.org/project/jieba/) 0.42.1 及以上。
    
    - [openpyxl](https://pypi.org/project/openpyxl/) 3.1.5 及以上。

在此向上述包的开发者表达感谢。

## 常见问题

Q：我遇到了问题/我有一个建议/我需要某个功能

A：请在[issue]()板块提出，或者给作者发邮件：wubzbz@126.com

## 更新日志

### 0.5.0: 2025/07/29



查看更多[更新日志](/docs/CHANGELOG.md)。

## 许可证

`yukkurimandarin` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
