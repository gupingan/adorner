import time
import random
from adorner import Decorator, Timer, Cacher, Retryer


# Decorator 的简单示例
# /////////////////////////////////////////////////////
@Decorator
def exception_decorator(self: Decorator):
    """
    捕获异常日志的装饰器
    :param self: 装饰器 Decorator 实例
    :return: 被修饰函数的执行结果
    """
    print(self.function_doc)  # 打印被装饰函数的文档
    print(self.decorator_doc)  # 打印装饰器的文档
    print(self.function_name)  # 打印被装饰函数的名称
    print(self.decorator_name)  # 打印装饰器的名称
    print(self.args)  # 打印被装饰函数的传入的位置参数 （默认形参值不包含）
    print(self.kwargs)  # 打印被装饰函数的传入的关键字参数  （默认形参值不包含）
    try:
        result = self.execute()  # 打印 1
        # 执行被装饰函数，不传入任何参数时，表示使用默认的参数 self.args、self.kwargs
        # 可覆盖传入参数
        self.execute(value=2)  # 打印 2
        self.execute(3)  # 打印3 并抛出异常
        return result
    except Exception as e:
        print(f"捕获异常: {e}")
        raise


@exception_decorator
def risky_function(value=1):
    print(value)
    if value == 3:
        raise ValueError("出错了")


try:
    risky_function()
except ValueError:
    pass  # 捕获异常: 出错了
"""打印如下：


    捕获异常日志的装饰器
    :param self: 装饰器 Decorator 实例
    :return: 被修饰函数的执行结果
    
risky_function
exception_decorator
()
{}
1
2
3
捕获异常: 出错了
"""

# Timer 的简单示例
# /////////////////////////////////////////////////////
timer = Timer()  # 可装饰多个函数，不过不太推荐（多个函数先后执行会覆盖掉计时器的元数据）


@timer
def my_function(a, b):
    """一个简单的函数，用于演示 Timer 装饰器的使用。"""
    time.sleep(1)  # 模拟一个耗时操作。
    return a + b


result = my_function(1, 2)
print(f'Execution result: {result}')
print(f"Execution time: {timer.time} seconds")
"""打印如下：
Execution result: 3
Execution time: 1.0067455 seconds
"""


# Cacher 的简单示例
# /////////////////////////////////////////////////////
@Cacher
def example1(x):
    """计算乘积"""
    return x * x


@Cacher
def example2(x):
    """计算和"""
    return x + x


print(example1)  # 打印：<Cacher: example>
# 正常调用
print(example1(4))  # 打印：16
# 打印函数的文档字符串
print(example1.function_doc)

# 缓存设置数据
example1.set('a', 1)
example1.set('b', 2)
example1.set('c', 3)

# example2.set('a', True)
# example2.set('b', False)
# 和上述一致
example2.sets(a=True, b=False, d='数据 d')

# 获取缓存数据
print(example1.get('a'))
print(example1.get('d', '数据不存在'))
# 检查 d 是否在缓存器 example1 中
print('d' in example1)

# 缓存数据合并
new_cacher = example1 + example2
print(new_cacher.data)  # 缓存器的所有数据
# 打印：{'a': True, 'b': False, 'c': 3, 'd': '数据 d'}

print(list(new_cacher))  # 将缓存器转为列表，可呈现存储的键

new_cacher += {'e': '合并的数据 e'}
# 迭代打印
for k, v in new_cacher.items():
    print(k, v)

# 批量获取数据
print(new_cacher.gets('a', 'b', 'z', default_value='没有这个数据'))
print(new_cacher.gets('a', 'b', 'c', filter_function=lambda x: x > 1))
# 如果比较类型不一致，可能会发生错误，比如下面这个例子：
# print(new_cacher.gets('a', 'b', 'c', 'd', filter_function=lambda x: x > 1))
# 解决方式：你可以自行捕捉，但是那样会很繁琐，推荐使用 filter_safe 参数
print(new_cacher.gets('a', 'b', 'c', 'd', filter_function=lambda x: x > 1, filter_safe=True))
# 如果启用了 filter_safe 参数还无法正常捕捉，请使用 filter_errors 指定异常，默认是 (TypeError, ValueError, KeyError, IndexError)
print(new_cacher.gets('a', 'b', 'c', 'd', filter_function=lambda x: x(),
                      filter_safe=True, filter_errors=(TypeError, ValueError, KeyError, IndexError)))

# 除了上述的 filter_function 参数，另外还有 map_function，同理也有 map_safe 以及 map_errors 参数
print(new_cacher.gets('a', 'b', 'c', map_function=lambda x: x > 1))
print(new_cacher.gets('a', 'b', 'c', 'd', map_function=lambda x: x > 1, map_safe=True))
print(new_cacher.gets('a', 'b', 'c', 'd', map_function=lambda x: x > 1, map_safe=True, map_errors=(TypeError,)))

# xxx_safe 参数的功能是当传入的函数执行发生异常时对应的一个处理，当出现异常时，该值对应的键值都不应存在于结果中
# 优先级别：正常获取值 -> filter筛选 -> map遍历处理 -> 返回结果

# 弹出某个值
print(new_cacher.pop('c'))
print(new_cacher.pop('c', default_value=None))  # 上面弹出了，这里尝试弹出一个不存在的，将返回 default_value（默认None）
print(new_cacher.pop('c') == new_cacher.pop('c', default_value=None))
print(new_cacher.data)  # {'a': True, 'b': False, 'd': '数据 d', 'e': '合并的数据 e'}

# 批量弹出
print(new_cacher.pops('b', 'c', default_value='不存在'))
print(new_cacher.data)  # {'a': True, 'd': '数据 d', 'e': '合并的数据 e'}

# 减法删除
sub = new_cacher - []  # 支持减去 字典 {'a', 任意值} 以及元组 ('a',)
print(sub.data)  # {'d': '数据 d', 'e': '合并的数据 e'}
print(new_cacher.data)  # {'d': '数据 d', 'e': '合并的数据 e'}

# Retryer 的简单示例
# /////////////////////////////////////////////////////
# 创建 Retryer 实例，设置捕获的异常类型为 KeyError，当被装饰的函数中出现该错误时将进行重试
retryer = Retryer(catches=[KeyError])


@retryer
def unreliable_function():
    """一个可能会抛出异常的函数，用于演示 Retryer 装饰器的使用"""
    option = random.randint(0, 2)
    if option == 0:
        raise KeyError('Random KeyError')
    elif option == 1:
        raise ValueError('Random ValueError')
    else:
        return "Success"


try:
    result = unreliable_function()
    print(result)
except Exception as e:
    print(f"Function failed after retries: {e}")

# 打印重试次数和捕获的异常
print(f"Retry count: {retryer.count}")
print(f"Exceptions: {retryer.exceptions}")
