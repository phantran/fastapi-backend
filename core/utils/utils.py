from typing import List

from core.config import config


def get_change(money_left: int) -> List:
    """
    Given an amount of money (sum), find the minimum number
    of counts that sum up to that value
    """
    for c in config.SUPPORTED_COINS:
        if money_left >= c:
            return [
                (int(money_left // c), c),
            ] + get_change(money_left % c)
    return []
