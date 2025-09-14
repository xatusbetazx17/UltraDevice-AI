def cap_with_cooldown(request_w: float, max_w: float, cooldown: float) -> float:
    # Simple cap; cooldown not modeled beyond parameter (placeholder)
    return min(request_w, max_w)
