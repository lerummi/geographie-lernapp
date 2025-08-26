import random
from typing import List, Tuple


def pick_random_record(data: List) -> Tuple:
    """
    Pick random item from data and remove item.
    """

    record = random.choice(data)
    data.remove(record)
    return record

