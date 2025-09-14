# 如何管理拼音数据库

## 0. 目录

- [建立数据库](#1-建立数据库)
- [增加/修改拼音数据](#2-增加修改拼音数据)
- [查询拼音数据](#3-查询拼音数据)
- [删除拼音数据](#4-删除拼音数据)
- [批量操作](#5-批量操作)


## 1. 建立数据库

对拼音数据库的所有操作方法都由数据库管理类`DatabaseManager`提供。通常情况下，使用默认方式创建`DatabaseManager`的实例会指向默认数据库，就像这样：

```python
import yukkurimandarin as ym

dm = ym.DatabaseManager()
```

`DatabaseManager`的实例可以作为参数`pinyin_database`提供给函数`text_convert()`以及`pinyin_convert()`，而它们将会基于这个数据库查询结果。

如果您想新建一个数据库而不是使用默认数据库的话，可以这样做：

```python
import yukkurimandarin as ym

dm = ym.DatabaseManager("my_database.db")
```

其中`my_database.db`是您想要建立的数据库的路径。如果这个文件不存在，对它操作前将创建一个空数据库；如果它存在，就可以通过`DatabaseManager`的实例`dm`对它进行操作。请确保数据库文件的后缀为`.db`。


## 2. 增加/修改拼音数据

```python
def add_pinyin(yinjie: str, tone: str, hiragana: str, report: bool = True) -> bool
```

一条拼音数据由3个基本元素构成：音节、声调和假名。

#### `yinjie`: 音节（字符串）

音节是不含声调的拼音，例如“hǎo”的音节为“hao”。

#### `tone`: 声调（字符串）

声调由3位0-5的数字组成，第一位是前一个字的声调，第二位是当前字的声调，第三位是后一个字的声调。0表示前面或后面没有字，1-5分别表示普通话四声和轻声。

#### `hiragana`: 假名拟音（字符串）

假名则是对应的假名拟音（含音声记号）。

#### `report`: 输出报告（布尔）

是否在终端输出报告信息。

请使用`DatabaseManager`的方法`add_pinyin`进行增加，例如：

```python
import yukkurimandarin as ym

dm = ym.DatabaseManager("my_database.db")

dm.add_pinyin("giao", "040", "ぎゃ'お")
```

上述操作在终端输出的信息将类似于

```
@ 2025-08-31 09:55:11 -- 操作:增加拼音数据 成功
|------|------|---------|
| 音节 | 声调 | 平假名  |
|------|------|---------|
| giao | 040  | ぎゃ'お |
|------|------|---------|
```

表格的显示效果因终端是否使用等宽字体而异。如果使用了不合法的声调，比如长度不等于3位、当前字的声调是0等，操作将失败：

```
@ 2025-08-31 10:04:12 -- 操作:增加拼音数据 失败
发生错误：声调 104 格式错误！
```

对已经存在于数据库中的拼音数据再次进行`add_pinyin`操作将修改它的值。


## 3. 查询拼音数据

```python
def search_by_pinyin(yinjie: str, 
                     tone: str = "***", 
                     report: bool = True) -> List[Tuple[str, str, str]]
```

查询时，通过音节和声调查找对应的假名拟音。

#### `yinjie`: 音节（字符串）

音节是不含声调的拼音，例如“hǎo”的音节为“hao”。

#### `tone`: 声调（字符串）

声调由3位0-5的数字组成，第一位是前一个字的声调，第二位是当前字的声调，第三位是后一个字的声调。0表示前面或后面没有字，1-5分别表示普通话四声和轻声。`*`是声调的通配符，也就是说，当某一位声调为`*`时，所有匹配的记录都会被选中。此参数的默认值是`***`，因此当您不填写它时，将会得到所有音节为`yinjie`的结果。

#### `report`: 输出报告（布尔）

是否在终端输出报告信息。

#### 返回值：搜索结果（字符串三元组列表）

搜索结果为按照`(yinjie, tone, hiragana)`格式组织的数据条目列表。

使用示例：

```python
import yukkurimandarin as ym

dm = ym.DatabaseManager("my_database.db")

dm.add_pinyin("giao", "124", "/ぎゃお")
dm.add_pinyin("giao", "144", "ぎゃ/お")
dm.add_pinyin("giao", "140", "ぎゃ'お")

# 使用tone的默认值（全通配）
dm.search_by_pinyin("giao")
# 精确指定tone
dm.search_by_pinyin("giao", "124")
# 使用通配符
dm.search_by_pinyin("giao", "1*4")
dm.search_by_pinyin("giao", "14*")
```


## 4. 删除拼音数据

```python
def delete_pinyin(yinjie: str, tone: str, report: bool = True) -> bool
```

通过音节和声调删除对应的假名拟音。

#### `yinjie`: 音节（字符串）

音节是不含声调的拼音，例如“hǎo”的音节为“hao”。

#### `tone`: 声调（字符串）

声调由3位0-5的数字组成，第一位是前一个字的声调，第二位是当前字的声调，第三位是后一个字的声调。0表示前面或后面没有字，1-5分别表示普通话四声和轻声。`*`是声调的通配符，也就是说，当某一位声调为`*`时，所有匹配的记录都会被删除。

#### `report`: 输出报告（布尔）

是否在终端输出报告信息。

#### 返回值：操作结果（布尔）

删除操作是否成功。

使用示例：

```python
import yukkurimandarin as ym

dm = ym.DatabaseManager("my_database.db")

dm.add_pinyin("giao", "124", "/ぎゃお")
dm.add_pinyin("giao", "144", "ぎゃ/お")
dm.add_pinyin("giao", "140", "ぎゃ'お")

# 精确指定tone
dm.delete_pinyin("giao", "124")
# 使用通配符
dm.delete_pinyin("giao", "1*4")
dm.delete_pinyin("giao", "14*")
# 使用全通配
dm.delete_pinyin("giao", "***")
```


## 5. 批量操作

上述方法适合进行小规模的增删查改操作，但当需要批量操作大量数据时，就会变得十分繁琐。因此，您可以选择将整个数据库导出到excel或csv文档，使用表格编辑软件对文档进行操作。编辑好的文档可以导入到数据库中。

### 5.1 生成文档

为了方便您了解数据库认可的xlsx和csv文档格式，同时帮助您通过导入文档方式构建数据库，本项目提供了利用内置函数生成数据文档的功能。它们的使用方法非常简单：

```python
def fill_csv(file_path: Optional[str] = None) -> None
```

```python
def fill_xlsx(file_path: Optional[str] = None) -> None
```

> [!NOTE]
> 使用`fill_xlsx()`前请确保`openpyxl`库已经安装。

#### `file_path`: 生成文件的路径（字符串）

设置您希望文件生成于何处。如果留空或为`None`，则导出到默认位置。

使用示例如下：

```python
import yukkurimandarin as ym

ym.fill_csv("my_filename.csv")
ym.fill_xlsx("my_filename.xlsx")
```

您可以自由地将导出的文件路径设置为您想要的，或者直接留空参数，导出到默认位置也可以。接着，您就可以使用合适的表格编辑工具打开生成的文档，进行查看、修改以及用于导入数据库了。


### 5.2 导出数据库到csv/xlsx文档

使用前文所述的`search_by_pinyin()`方法检查数据库中的特定拼音数据虽然快捷，但当需要批量查看、修改数据时，操作将会变得十分繁琐。因此，您可以将整个数据库导出到一个表格文档中，再用您的表格编辑软件进行查看、修改。

```python
def export_to_csv(file_path: Optional[str] = None, report: bool = True) -> bool
```

```python
def export_to_excel(file_path: Optional[str] = None, report: bool = True) -> bool
```

> [!NOTE]
> 使用`export_to_excel()`前请确保`openpyxl`库已经安装。

#### `file_path`: 生成文件的路径（字符串）

设置您希望文件生成于何处。如果留空或为`None`，则导出到默认位置。

使用示例：

```python
import yukkurimandarin as ym

dm = ym.DatabaseManager("my_database.db")

dm.add_pinyin("an", "115", "あん")
dm.add_pinyin("an", "132", "'あん")
dm.add_pinyin("an", "144", "あ/ん")

dm.export_to_csv("my_table.csv")
dm.export_to_excel("my_table.xlsx")
```

请查看导出的`my_table.csv`以及`my_table.xlsx`（如果安装了`openpyxl`），其内容将类似：

```
拼音,声调,平假名
an,115,あん
an,132,'あん
an,144,あ/ん
```


### 5.3 从csv/xlsx文档导入数据

拼音数据库可以从现有的csv或excel表格中批量导入数据。

```python
def import_from_csv(file_path: Optional[str] = None, report: bool = True) -> bool
```

```python
def import_from_excel(file_path: Optional[str] = None, report: bool = True) -> bool
```

> [!NOTE]
> 使用`import_from_excel()`前请确保`openpyxl`库已经安装。

#### `file_path`: 生成文件的路径（字符串）

设置您希望文件生成于何处。如果留空或为`None`，则从默认位置导入。

使用方法示例（假设my_table.csv和my_table.xlsx存在且格式正确）：

```python
import yukkurimandarin as ym

dm = ym.DatabaseManager("my_database.db")

dm.import_from_csv("my_table.csv")
dm.import_from_excel("my_table.xlsx")
```

推荐您使用[5.1节](#51-生成文档)和[5.2节](#52-导出数据库到csvxlsx文档)中提到的生成/导出的表格文档进行导入。否则的话，请确保将要导入的表格文档的格式符合以下要求：

- 文件后缀：csv文档为`.csv`，excel文档为`.xlsx`；
- 必须包含3列数据，表头依次为"拼音", "声调", "平假名"；
- 当excel文档包含多个工作表时，只会尝试从当前活动工作表导入数据。

如果某行数据存在格式错误、值缺失等问题，将会导入失败，但不会影响其他行数据的导入。例如准备以下csv文档并尝试导入数据库：

```
拼音,声调,平假名
an,115,あん
an,132,
an,104,あ/ん
```

其中第2行数据存在缺失、第3行数据的声调格式错误。此时导入将得到类似以下信息：

```
@ 2025-09-12 11:58:08 -- 操作:从csv导入拼音数据库 失败
第 2 行: 缺少必填字段
第 3 行: 声调104格式错误
导入完成。成功: 1, 失败: 2
```

从提示信息中，您可以轻松定位导入失败的数据所在的行数以及问题描述，从而精准修改。即使第2、3行导入失败，也不会影响其他正确的数据行（如第1行）的导入。


### 5.4 使用默认路径的最佳实践

下面提供一个检修数据库的实践案例。

#### 步骤一：导出表格

```python
import yukkurimandarin as ym

dm = ym.DatabaseManager("my_database.db")

dm.export_to_csv()
```

连接您希望进行操作的数据库，例如`my_database.db`。将其中的内容导出到默认位置`yinjie_table.csv`。

#### 步骤二：编辑表格

您只需在当前目录中找到并打开表格文档`yinjie_table.csv`并进行编辑，然后保存文档。

#### 步骤三：重新导入

```python
import yukkurimandarin as ym

dm = ym.DatabaseManager("my_database.db")

dm.import_from_csv()
```

将编辑好的文档重新导入数据库。如果您不放心，可再次导出数据至文档进行检查。


### 5.5 涉及删除的批量操作

请您注意，本节所述的方法只便利了数据库的批量增加、查询、修改操作。从文档导入数据时，各种情况的操作结果如下：

- 数据库中不存在，而文档中存在的数据：在数据库中新增数据；
- 数据库中存在，而文档中也存在相同的数据：保持原样；
- 数据库中存在，而文档中存在不相同的数据：修改数据库中的数据；
- 数据库中存在，而文档中不存在的数据：保持原样。

敬请注意最后一条规则，这意味着您不可以通过“导出文档—删除数据—重新导入”的方式实现数据库的删除操作。举例说明，假设数据库内原有A、B、C三条数据；导出文档后，删除文档中的数据B，得到只含数据A、C的文档；将此文档导入数据库将不会导致数据库中的B删除。

因此，建议您在删除少量数据时使用`delete_pinyin()`。在批量删除数据时，请按以下步骤操作：

1. 将数据库中的数据导出到表格文档；
2. 在表格文档中删除不需要的数据；
3. 新建一个`DatabaseManager`的实例，指向一个新数据库；
4. 将文档导入到新数据库中；
5. 如果您确定不再需要原来的数据库，手动删除它。