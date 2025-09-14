import pytest
from pydantic import ValidationError
from ultradevice.models import PowerProfile

def test_validation():
    with pytest.raises(ValidationError):
        PowerProfile(battery_wh=-1, avg_load_w=1.0)
