"""
LRU (Least Recently Used) Dictionary implementation.

Provides a dictionary with automatic eviction of least recently used items
when the maximum size is reached.
"""
from collections import OrderedDict


class LRUDict(OrderedDict):
    """
    A dictionary that maintains a maximum size by evicting least recently used items.

    When the dictionary reaches max_size and a new item is added, the oldest
    (least recently accessed) item is automatically removed.

    Args:
        max_size: Maximum number of items to store in the dictionary
    """

    def __init__(self, max_size: int):
        super().__init__()
        self.max_size = max_size

    def __setitem__(self, key, value):
        # If key exists, remove and re-insert to mark it as most recently used
        if key in self:
            del self[key]
        elif len(self) >= self.max_size:
            # Pop the least recently used item (first inserted)
            self.popitem(last=False)
        super().__setitem__(key, value)

    def get(self, key, default=None):
        if key in self:
            value = self.pop(key)
            self[key] = value  # Re-insert to mark as most recently used
            return value
        return default