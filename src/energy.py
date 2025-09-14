def cap_with_cooldown(request_w: float, max_w: float, cooldown: float) -> float:
    return min(request_w, max_w)
