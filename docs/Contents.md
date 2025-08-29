# 油库里普通话功能详解


## 目录

- [文字转换](#文字转换)
- [拼音转换](#拼音转换)


## 文字转换

### 基础用法

文字转换功能将中文句子转换为“伪日本语”。示例：

```python
import yukkurimandarin as ym

result = ym.text_convert("油库里普通话。")
print(result)
```

此代码的输出将类似于

```
/ようく'うりい'ぷ/うとんふ'あ。
```

复制输出的内容，将其粘贴到支持[音声记号](https://github.com/wubzbz/Yukkuri-Mandarin/blob/main/docs/phonology.md/#什么是音声记号)的油库里语音生成器中，即可生成中文油库里语音。

#### 一、（推荐）在[油库里MovieMaker](https://manjubox.net/ymm4/)中使用

![图片不见了咯](https://github.com/wubzbz/Yukkuri-Mandarin/blob/main/docs/Asset/eg-ymm4.png)

首先在时间轴选中语音物件，将生成的“伪日本语”粘贴到右侧物件编辑面板—“语音”—“发音”文本框中。**请注意是“发音”文本框**而不是“台词”文本框。然后点击右侧的播放按钮，确认生成的语音是否符合要求。


#### 二、在[AquesTalkPlayer](https://www.a-quest.com/products/aquestalkplayer.html)中使用

在AquesTalkPlayer中使用音声记号标记的文本时，需要在其开头加上`#>`。要实现这一点非常简单，只需要稍微修改一下你的代码：

```python
import yukkurimandarin as ym

result = ym.text_convert("油库里普通话。")
print(f"#>{result}") # 使用f-字符串为伪日本语的开头添加#>
```

接着，将生成的“伪日本语”粘贴到文本框中，点击Play即可播放。如下图所示：

![图片不见了咯](https://github.com/wubzbz/Yukkuri-Mandarin/blob/main/docs/Asset/eg-aquestalk.png)

#### 三、注意事项

- 如果您使用上述语音生成软件以外的生成工具，请确认其是否支持音声记号。如果不支持，可以设置`text_convert`的参数`without_accent`为`True`，以获得不含音声记号的结果。
- 如果您使用的语音生成工具对音声记号的定义与本项目采用的不一致，您可以选择[自建拼音数据库](https://github.com/wubzbz/Yukkuri-Mandarin/blob/main/docs/database-mngr.md)。
- 有时候会出现无法生成语音的情况。请首先检查生成的“伪日本语”中是否包含语音转换工具不支持的字符。例如，一些终端在输出结果时，会自动为行末的半角字符位补一个**空格**以满足行宽。如果您采用复制终端输出的方法，请检查是否包含这种多余的空格。考虑到这种情况，更建议您采用将结果输出到文件中再复制的方式。

### 高级用法

![原理图（深色）](https://github.com/wubzbz/Yukkuri-Mandarin/blob/main/docs/Asset/UML-d.png#gh-dark-mode-only)

![原理图（浅色）](https://github.com/wubzbz/Yukkuri-Mandarin/blob/main/docs/Asset/UML-l.png#gh-light-mode-only)

```python
def text_convert(sentence: str, 
                 without_accent: bool = False,
                 tokenizer: Optional["Tokenizer"] = None, 
                 pinyin_database: Optional[DatabaseManager] = None,
                 non_hanzi_config: Optional[NonHanziModes] = None) -> str:
```

#### `sentence`: 待转换的汉字句子（字符串）

中文句子。包含阿拉伯数字也可以。不超过13位的数字都可以读出来，例如`666`会被读作“六百六十六”。如果想让数字像电话号码那样一个一个地念出来，请在数字的末尾加上一个空格，如`666 `则会读作“六六六”。任何以0开头，或者整数位超过13位的数字也会以这种方式读出来。

#### `without_accent`: 是否去除音声记号（布尔）

如果设置为`True`，则输出的结果不会包含音声记号。

```python
import yukkurimandarin as ym

result1 = ym.text_convert("你干~嘛？哎哟！", without_accent=False)
result2 = ym.text_convert("你干~嘛？哎哟！", without_accent=True)

print("含音声记号：", result1)
print("不含音声记号：", result2)
```

您可以通过上面这个示例进行试验，结果应该类似于：

```
含音声记号： 'に/いが'ん、/っまあ?/っあいよお。
不含音声记号： にいがん、っまあ?っあいよお。
```

#### `tokenizer`: jieba分词器

> [!NOTE]
> 使用此参数前请确保`jieba`库已经安装。

来自`jieba`库的`Tokenizer`类。您可以初始化一个`Tokenizer`类的实例作为此参数传入，这意味着您可以通过自定义词典等方式优化分词，提高读音准确性。例如：

```python
from jieba import Tokenizer
import yukkurimandarin as ym

# 创建Tokenizer实例
my_tokenizer = Tokenizer()
# 添加自定义词语
my_tokenizer.add_word("参差不齐")
# 加载自定义词典文件
my_tokenizer.load_userdict("user_dict.txt")

result = ym.text_convert("普通人参差不齐的水平", tokenizer=my_tokenizer)
print(result)
```

更详细的用法介绍请查阅[jieba文档](https://github.com/fxsjy/jieba)。

#### `pinyin_database`: 拼音数据库

`DatabaseManager`类的实例。通过此参数，您可以在转换过程中使用您自己的数据库而不是默认数据库。例如：

```python
import yukkurimandarin as ym

# 使用自建数据库
my_db = ym.DatabaseManager("my_database.db")

result = ym.text_convert("两块钱一斤。", pinyin_database=my_db)
print(result)
```

详情请见[拼音数据库管理](https://github.com/wubzbz/Yukkuri-Mandarin/blob/main/docs/database-mngr.md)。

#### `non_hanzi_config`: 非汉字字符处理模式

如原理图所示，非汉字字符大致可以分为英文字母（en）、日语假名（ja）、标点符号（pc）以及其他符号（other）四种。对于各种非汉字字符，准备了4种处理模式（mode）：

- `ignore`: 忽略掉非汉字片段
- `keep`: 保留非汉字片段
- `replace`: 用自定义字符串代替非汉字片段
- 可调用的函数：用于处理非汉字片段

比如，假设需要忽略掉英文字母而保留假名，可以这样做：

```python
import yukkurimandarin as ym

my_config = ym.NonHanziModes(en_mode="ignore", ja_mode="keep")

result = ym.text_convert("He said: こんにちは！", non_hanzi_config=my_config)
print(result)
```

其中用于初始化`NonHanziModes`类的参数`en_mode`和`ja_mode`分别表示英文字母和日语假名的处理模式。以此类推，`pc_mode`和`other_mode`分别代表标点符号和其他字符的处理模式。

使用替换（replace）模式需要搭配用于替换的字符串变量使用。如果想要把英文片段替换为`@`，可以这么做：

```python
import yukkurimandarin as ym

my_config = ym.NonHanziModes(en_mode="replace", en_replace="@")

result = ym.text_convert("city不city", non_hanzi_config=my_config)
print(result)
```

其中，`NonHanziModes`类的参数`en_replace`即所有英文字母片段将被替换为的字符串。同样的，在使用替换模式时，`ja_replace`、`pc_replace`和`other_replace`分别代表日语假名、标点符号和其他字符片段将被替换为的字符串。

您还可以定义更复杂的非汉字字符处理逻辑。这可以通过传入可调用的函数来实现。假如您需要将英文字母大写化，可以这样实现：

```python
import yukkurimandarin as ym

def to_upper(fragment):
    return fragment.upper()

my_config = ym.NonHanziModes(en_mode=to_upper)

result = ym.text_convert("city不city", non_hanzi_config=my_config)
print(result)
```

在上面这个例子中，我们定义了一个函数`to_upper`，用于将英文片段大写化，并将其作为`NonHanziModes`类的参数`en_mode`。您也可以为其他类型的字符设计它们的专属处理函数，只需确保您的函数接受一个字符串参数，且返回值也是一个字符串即可。

最后，`global_mode`和`global_replace`分别设置了全局处理模式和全局替换字符。这两个参数作用于所有种类的非汉字字符，除非您为某个种类单独设置了参数。如下面例子所示：

```python
import yukkurimandarin as ym

def to_upper(fragment):
    return fragment.upper()

my_config = ym.NonHanziModes(en_mode=to_upper, global_mode="replace", global_replace="@")

result = ym.text_convert("city不city?", non_hanzi_config=my_config)
print(result)
```

在这种情况下，对于英文片段将大写化处理，除英文字母外的其他非汉字字符将被替换为`@`。

> [!TIP]
> 如果保持参数`non_hanzi_config`为其默认值`None`，则`text_convert`对非汉字字符的处理模式为：对标点符号使用内置函数处理转化为音声记号，日语假名则统一转化为平假名。如果您对此感兴趣，请查阅源代码[non_hanzi_process.py](https://github.com/wubzbz/Yukkuri-Mandarin/blob/main/yukkurimandarin/non_hanzi_process.py)。


## 拼音转换

### 基础用法

拼音转换允许将以空格分开的拼音序列转换为“伪日本语”。

使用拼音转换函数可以让您更自由地掌握音节和音调，这在某些需要特殊发音的场景特别有效。您甚至可以通过数据库管理模块添加特殊发音，实现无对应汉字的音节转换（例如`giao`）。

但另一方面，您的输入需要严格遵守拼音序列的格式——以空格分割各个拼音、使用音节+数字声调的格式表示拼音。

### 高级用法


