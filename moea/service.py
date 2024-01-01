from typing import (Any, Callable, Dict, Iterable, List, NamedTuple, Optional,
                    Set, Tuple, Union)
from moea import trigger


class ServiceFunc:
    def __init__(self, sv: "Service", func: Callable, only_to_me: bool, normalize_text: bool=False):
        self.sv = sv
        self.func = func
        self.only_to_me = only_to_me
        self.normalize_text = normalize_text
        self.__name__ = func.__name__

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


class Service:
    def __init__(self, name):
        self.name = name

    def on_prefix(self, *prefix, only_to_me=False) -> Callable:
        if len(prefix) == 1 and not isinstance(prefix[0], str):
            prefix = prefix[0]
        def deco(func) -> Callable:
            sf = ServiceFunc(self, func, only_to_me)
            for p in prefix:
                if isinstance(p, str):
                    trigger.prefix.add(p, sf)
                else:
                    # self.logger.error(f'Failed to add prefix trigger `{p}`, expecting `str` but `{type(p)}` given!')
                    print(f'Failed to add prefix trigger `{p}`, expecting `str` but `{type(p)}` given!')
            return func
        return deco