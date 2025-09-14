def emergency_allowed(temp_c: float, max_temp_c: float, time_in_boost_s: float, max_boost_s: float) -> bool:
    return temp_c <= max_temp_c and time_in_boost_s <= max_boost_s
