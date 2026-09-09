from .config import Scenario
from .profiles import load_hourly_csv


def validate_scenario(scn: Scenario):
    errors = []
    profiles = []
    if scn.harvest.solar:
        profiles.append((scn.harvest.solar.irradiance_csv, 0, None))
    if scn.harvest.kinetic:
        profiles.append((scn.harvest.kinetic.motion_csv, 0, None))
    if scn.ambient_csv:
        profiles.append((scn.ambient_csv, -40, 85))
    if scn.cloudiness_csv:
        profiles.append((scn.cloudiness_csv, 0, 1))
    for path, low, high in profiles:
        try:
            load_hourly_csv(path, minimum=low, maximum=high)
        except (OSError, ValueError) as error:
            errors.append(str(error))
    return errors
