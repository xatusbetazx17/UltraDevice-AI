"""Digital boost eligibility only; no physical transformation."""
from .validation import number


def emergency_allowed(temp_c, max_temp_c, time_in_boost_s, max_boost_s):
    number("temp_c", temp_c, minimum=-273.15, positive=True)
    number("max_temp_c", max_temp_c, minimum=-273.15, positive=True)
    number("time_in_boost_s", time_in_boost_s)
    number("max_boost_s", max_boost_s, positive=True)
    return temp_c < max_temp_c and time_in_boost_s < max_boost_s
