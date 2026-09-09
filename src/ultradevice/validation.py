"""Shared numeric validation for public engineering utilities."""
import math


def number(name, value, *, minimum=0.0, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number")
    if not math.isfinite(value) or value < minimum or (positive and value == minimum):
        relation = ">" if positive else ">="
        raise ValueError(f"{name} must be finite and {relation} {minimum}")
    return value


def efficiency(name, value):
    number(name, value, positive=True)
    if value > 1:
        raise ValueError(f"{name} must be <= 1")
    return value
