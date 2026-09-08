"""Enumeration of all standard player decisions and actions in Blackjack."""

from enum import Enum


class Action(str, Enum):
    """Player actions in a blackjack round."""

    HIT = "HIT"
    STAND = "STAND"
    DOUBLE = "DOUBLE"
    SPLIT = "SPLIT"
    SURRENDER = "SURRENDER"
    INSURANCE = "INSURANCE"
    NO_INSURANCE = "NO_INSURANCE"

    def __str__(self) -> str:
        return self.value
