# 安装方式


## 从Pypi安装

最经典的安装方法。首先确保您的设备上安装了python解释器(版本至少为3.9)和pip。

在终端输入如下命令将安装yukkuri-mandarin包以及两个可选依赖包，获得最完整的体验：

```bash
pip install yukkuri-mandarin[jieba, openpyxl]
```

如果因为某种原因不能安装可选依赖包，您可通过以下方式安装：

```bash
pip install yukkuri-mandarin
```

或者仅安装一个可选依赖包：

```bash
pip install yukkuri-mandarin[jieba]
```

```bash
pip install yukkuri-mandarin[openpyxl]
```

如果您是想升级，请运行以下命令：

```bash
pip install --upgrade yukkuri-mandarin
```


## 从本地wheel发行文件安装

### 下载`.whl`文件

访问本项目的[PyPI页面](https://pypi.org/project/yukkuri-mandarin/)或者[GitHub Release页面](https://github.com/wubzbz/yukkuri-mandarin/releases)，下载最新版本的`.whl`文件。

[pic1]
[pic2]

### 本地安装

下载完成后，在终端中执行以下命令进行安装：

```bash
pip install yukkuri-mandarin-<版本号，比如1.2.0>-py3-none-any.whl
```
> [!IMPORTANT]
> 请将`yukkuri-mandarin-x.x.x-py3-none-any.whl`替换为您实际下载的文件名。

## 从本地源码发行文件安装

### 下载`.tar.gz`文件

从项目的[PyPI页面](https://pypi.org/project/yukkuri-mandarin/)或[GitHub Release页面](https://github.com/wubzbz/yukkuri-mandarin/releases)下载源码压缩包（通常命名为`yukkuri-mandarin-x.x.x.tar.gz`）。

[pic3]
[pic4]

### 本地编译安装

1. 解压下载的源码包：
```bash
tar -xzf mypack-x.x.x.tar.gz
cd mypack-x.x.x
```

2. 使用pip进行安装（推荐，跨平台兼容）：
```bash
pip install .
```

或者使用setuptools安装：
```bash
python setup.py install
```

## 从GitHub源码编译发行文件

### 克隆仓库到本地

```bash
git clone https://github.com/yourusername/mypack.git
cd mypack
```

### 安装依赖项

项目依赖列在`requirements.txt`文件中：

```bash
pip install -r requirements.txt
```

### 构建发行文件

#### 使用build工具（推荐）

1. 首先安装build工具：
```bash
pip install build
```

2. 构建发行文件：
```bash
python -m build
```

此命令会在`dist/`目录下生成`.whl`和`.tar.gz`发行文件。

#### 使用Poetry

如果使用Poetry管理：

1. 安装Poetry：


2. 构建发行文件：

```bash
poetry build
```

构建完成后，您可以使用前述方法安装生成的发行文件。

---

**注意**：如果您不确定安装是否会带来依赖项冲突，建议在虚拟环境中进行安装，以避免与系统Python环境冲突。可以使用`venv`或`virtualenv`创建虚拟环境：

```bash
# 创建虚拟环境
python -m venv myenv

# 激活虚拟环境（Linux/macOS）
source myenv/bin/activate

# 激活虚拟环境（Windows）
myenv\Scripts\activate
```



