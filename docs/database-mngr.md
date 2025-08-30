# 如何管理拼音数据库

## 0. 目录

- [建立数据库](#1-建立数据库)
- 


## 1. 建立数据库

对拼音数据库的所有操作方法都由数据库管理类`DatabaseManager`提供。通常情况下，使用默认方式创建`DatabaseManager`的实例会指向默认数据库，就像这样：

```python
import yukkurimandarin as ym

dm = ym.DatabaseManager()
```

`DatabaseManager`的实例可以作为参数`pinyin_database`提供给函数`text_convert`以及`pinyin_convert`，而它们将会基于这个数据库查询结果。

如果您想新建一个数据库而不是使用默认数据库的话，可以这样做：

```python
import yukkurimandarin as ym

dm = ym.DatabaseManager("my_database.db")
```

其中`my_database.db`是您想要建立的数据库的路径。如果这个文件不存在，将创建一个空数据库；如果它存在，就可以通过实例`dm`对它进行操作。请确保数据库文件的后缀为`.db`。

## 2. 增加拼音数据

一条拼音数据由3个基本元素构成：音节、声调和假名。音节是不含声调的拼音，例如“hǎo”的音节为“hao”。