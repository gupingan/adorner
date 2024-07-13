import functools
import time
import typing as t


class Decorator(object):
    def __init__(self, decorator=None):
        self.decorator = decorator or (lambda s: s.execute())
        self.function = None
        self.args = tuple()
        self.kwargs = dict()

    def __call__(self, function):
        """
        将装饰器应用于函数
        :param function: 要装饰的函数
        :return: 装饰后的函数
        """

        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            self.function = function
            self.args = args
            self.kwargs = kwargs
            return self.decorator(self)

        return wrapper

    def __repr__(self):
        """
        返回对象的字符串表示形式
        :return: 字符串形式的对象表示
        """
        decorator_name = self.decorator_name.lstrip('<').rstrip('>')
        if self.function:
            return f'<{self.__class__.__name__}: {decorator_name} To {self.function.__name__}>'
        return f'<{self.__class__.__name__}: {decorator_name}>'

    def execute(self, *args, **kwargs):
        """
        执行被装饰的函数
        :param args: 传递给被装饰函数的位置参数
        :param kwargs: 传递给被装饰函数的关键字参数
        :return: 被装饰函数的返回值
        """
        final_args = args if args else self.args
        final_kwargs = kwargs if kwargs else self.kwargs
        return self._execute_sync(final_args, final_kwargs)

    def _execute_sync(self, args, kwargs):
        """
        同步执行被装饰的函数
        :param args: 传递给被装饰函数的位置参数
        :param kwargs: 传递给被装饰函数的关键字参数
        :return: 被装饰的函数的返回值
        """
        return self.function(*args, **kwargs)

    @property
    def function_name(self):
        """返回被装饰函数的名称"""
        if self.function:
            return self.function.__name__
        return '<None>'

    @property
    def function_doc(self):
        """返回被装饰函数的文档字符串"""
        if self.function:
            return self.function.__doc__ or ''
        return ''

    @property
    def decorator_name(self):
        """返回装饰器的名称"""
        if self.decorator:
            return self.decorator.__name__
        return '<None>'

    @property
    def decorator_doc(self):
        """返回装饰器的文档字符串"""
        if self.decorator:
            return self.decorator.__doc__ or ''
        return ''


class Timer(Decorator):
    def __init__(self, decorator=None):
        super().__init__(decorator)
        self.time = 0

    def execute(self, *args, **kwargs):
        """
        执行被装饰的函数，并记录其执行时间。
        :param args: 传递给被装饰函数的位置参数
        :param kwargs: 传递给被装饰函数的关键字参数
        :return: 被装饰的函数的返回值
        """
        _start = time.perf_counter()
        result = super().execute(*args, **kwargs)
        _end = time.perf_counter()
        self.time = _end - _start
        return result


class Cacher:
    hash = dict()

    def __new__(cls, function):
        if function in cls.hash:
            instance = cls.hash[function]
        else:
            instance = object.__new__(cls)
            instance.function = function
            instance.data = dict()
            setattr(instance, '__name__', f'{cls.__name__}-{function.__name__}')
            cls.hash[function] = instance

        return instance

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.function.__name__}>'

    def __iter__(self):
        """使 Cacher 实例可迭代，迭代缓存数据"""
        return iter(self.data)

    def __contains__(self, item):
        """判断缓存数据中是否包含指定的键"""
        return item in self.data

    def __add__(self, other):
        """支持使用 + 运算符合并缓存数据"""
        if isinstance(other, self.__class__):
            self.data.update(other.data)
            return self
        if isinstance(other, dict):
            self.data.update(other)
            return self
        if isinstance(other, (tuple, list)):
            self.data.update(dict(other))
            return self
        raise TypeError(f'unsupported operand type(s) for +: \'{type(self)}\' and \'{type(other)}\'')

    def __sub__(self, other):
        """支持使用 - 运算符从缓存数据中删除指定的键"""
        if isinstance(other, self.__class__):
            for key in other.data:
                self.data.pop(key, None)
            return self
        if isinstance(other, dict):
            for key in other:
                self.data.pop(key, None)
            return self
        if isinstance(other, (tuple, list)):
            self.pops(*other)
            return self
        raise TypeError(f'unsupported operand type(s) for -: \'{type(self)}\' and \'{type(other)}\'')

    def items(self):
        return self.data.items()

    def set(self, key, value, safe=False):
        """
        设置缓存数据
        :param key: 键
        :param value: 值
        :param safe: 如果为 True，则只有在 key 不存在的情况下才设置值
        :return:
        """
        if not safe:
            self.data[key] = value
        elif key not in self.data:
            self.data[key] = value

        return self.data[key]

    def sets(self, **data_dict):
        """批量设置缓存数据"""
        self.data.update(data_dict)

    def get(self, key, default_value=None):
        """
        获取缓存数据
        :param key: 键
        :param default_value: 键不存在时返回的值，默认 None
        :return: 键对应的值或者 None
        """
        return self.data.get(key, default_value)

    @staticmethod
    def _apply_filter(values, filter_function, filter_safe, filter_errors):
        """应用筛选函数"""
        def safe_filter(value):
            try:
                return filter_function(value)
            except filter_errors:
                return False

        filter_func = safe_filter if filter_safe else filter_function
        return {key: value for key, value in values.items() if filter_func(value)}

    @staticmethod
    def _apply_map(values, map_function, map_safe, map_errors):
        """应用遍历处理的函数"""
        def safe_map(value_):
            try:
                return True, map_function(value_)
            except map_errors:
                return False, None

        if map_safe:
            new_values = {}
            for key, value in values.items():
                success, mapped_value = safe_map(value)
                if success:
                    new_values[key] = mapped_value
            return new_values
        else:
            return {key: map_function(value) for key, value in values.items()}

    def gets(self, *keys, default_value=None,
             filter_function=None, filter_safe=False, filter_errors=None,
             map_function=None, map_safe=False, map_errors=None):
        """
            批量获取缓存数据
            支持通过 filter_function 过滤值，通过 map_function 处理值
        """

        values = {key: self.data.get(key, default_value) for key in keys}

        if filter_function:
            filter_errors = filter_errors or (TypeError, ValueError, KeyError, IndexError)
            values = self._apply_filter(values, filter_function, filter_safe, filter_errors)

        if map_function:
            map_errors = map_errors or (TypeError, ValueError, KeyError, IndexError)
            values = self._apply_map(values, map_function, map_safe, map_errors)

        return values

    def pop(self, key, default_value=None):
        """
        删除并返回缓存数据中的指定键的值
        如果键不存在，则返回 default_value 的值
        """
        return self.data.pop(key, default_value)

    def pops(self, *keys, default_value=None):
        """
        批量删除并返回缓存数据中的指定键的值列表
        如果键不存在，则返回的列表中对应的值为 default_value
        """
        return [self.data.pop(key, default_value) for key in keys]

    @property
    def function_name(self):
        """返回被装饰函数的名称"""
        if self.function:
            return self.function.__name__
        return '<None>'

    @property
    def function_doc(self):
        """返回被装饰函数的文档字符串"""
        if self.function:
            return self.function.__doc__ or ''
        return ''


class Retryer:
    def __init__(self, max_retry: t.Union[int] = 3, delay: t.Union[int] = 0, catches: t.List[Exception] = None):
        """
        Retryer 实例化

        :param max_retry: 最大重试次数，默认为 3
        :param delay: 每次重试之间的延迟时间（秒），默认为 0
        :param catches: 需要捕获的异常类型列表，默认为空列表
        """
        self.max_retry = max_retry
        self.delay = delay
        self.catches = catches or []
        self.exceptions = []  # 执行过程中捕捉到的异常
        self.count = 0  # 执行中发生了几次重试

    def __call__(self, function):
        """使 Retryer 实例可作为装饰器使用。"""
        return Decorator(self.run)(function)

    def run(self, decorator: Decorator):
        """
        执行重试逻辑。

        :param decorator: 包装的装饰器对象。
        :return: 被装饰函数的返回值。
        """
        _catch_exceptions = tuple(self.catches) if self.catches else Exception
        self.exceptions.clear()
        i = 0
        while i <= self.max_retry:
            self.count = i
            try:
                result = decorator.execute()
            except _catch_exceptions as e:
                self.exceptions.append(e)
                i += 1
                if i <= self.max_retry:
                    time.sleep(self.delay)
                continue
            else:
                return result
