"""Compatibility utility; cooldown means seconds remaining before another boost."""
from .validation import number


def cap_with_cooldown(request_w, max_w, cooldown):
    for name, value in (("request_w", request_w), ("max_w", max_w), ("cooldown", cooldown)):
        number(name, value)
    return 0.0 if cooldown > 0 else min(request_w, max_w)
