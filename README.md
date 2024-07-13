## 简述

`adorner` 是一个现代轻量级 Python 装饰器辅助模块。

本项目采用 MIT 许可证。请查看 [LICENSE](LICENSE) 文件以了解更多信息。

## 特性

- 充分利用 Python 面向对象的基本语法
- 内置 4 个常用的辅助类，具备以下功能：
  - `Decorator`：标记装饰器函数，使装饰器的构造更简单
  - `Timer`：函数计时装饰器类
  - `Cacher`：函数缓存装饰器类
  - `Retryer`：函数异常重试处理类

- 为上层开发者提供更便利、灵活的装饰器辅助，让代码更少、更精

## 安装

### 1. 本地

如果您不想从源代码安装，您可以直接安装发布到 GitHub Releases 页面的打包版本。

首先，下载最新的发布包 `gpa-obscuror-x.x.x.tar.gz` 从 [GitHub Releases](https://github.com/gupingan/adorner/releases) 页面。

接着，您可以使用 pip 等包管理工具来安装下载的 `.tar.gz` 文件：

```bash
pip install ./adorner-x.x.x.tar.gz
```

其中 `x.x.x` 为您下载 `.tar.gz` 文件确版本，并确保指定安装包文件路径是正确的。

### 2. 网络

```bash
pip install adorner
```

假如上述命令执行后发生了一些错误，可以选择使用`pip3`命令或者添加镜像源等等方式解决。

## 快速使用

安装完本模块后，您可以按照以下方式使用 `adorner`：

```python
from adorner import Decorator


@Decorator
def timing_decorator(self: Decorator):
    """
    记录执行时间的装饰器
    :param self: 装饰器 Decorator 实例
    :return: 被修饰函数的执行结果
    """
    start_time = time.perf_counter()
    result = self.execute()
    end_time = time.perf_counter()
    print(f"执行时间: {end_time - start_time:.8f} 秒")
    return result


@Decorator
def exception_decorator(self: Decorator):
    """
    捕获异常日志的装饰器
    :param self: 装饰器 Decorator 实例
    :return: 被修饰函数的执行结果
    """
    try:
        result = self.execute()
        return result
    except Exception as e:
        print(f"捕获异常: {e}")
        raise
    

@timing_decorator
@exception_decorator
def process_data(data, sleep: int = 0):
    if sleep:
        time.sleep(sleep)
    if not data:
        raise ValueError("数据不能为空")
    print(f"处理数据: {data}")
    return f"结果: {data}"


result = process_data("有效数据")  # 正常的执行
print(result)
process_data("")  # 试错
```

如果你想要了解更多的使用案例，请参考这篇文章：[adorner 使用示例](https://www.cnblogs.com/gupingan/p/18299851)