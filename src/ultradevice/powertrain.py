from .validation import efficiency, number


def signed_net_draw(load_w, harvest_w, eff_out=0.90, eff_harv=0.80):
    """Battery-side power: positive discharges, negative charges."""
    number("load_w", load_w)
    number("harvest_w", harvest_w)
    efficiency("eff_out", eff_out)
    efficiency("eff_harv", eff_harv)
    return load_w / eff_out - harvest_w * eff_harv


def effective_net_draw(load_w, harvest_w, eff_out=0.90, eff_harv=0.80):
    """Compatibility helper returning discharge only."""
    return max(0.0, signed_net_draw(load_w, harvest_w, eff_out, eff_harv))
