"""TMP117 driver uses signed 16-bit temperature register 0x00, 1/128 C per LSB."""


class TMP117:
    def __init__(self, i2c, address=0x48):
        self.i2c = i2c
        self.address = address
        identity = self.i2c.readfrom_mem(address, 0x0F, 2)
        if (int.from_bytes(identity, "big") & 0x0FFF) != 0x0117:
            raise ValueError("TMP117 identity mismatch")

    def temperature_c(self):
        raw = self.i2c.readfrom_mem(self.address, 0x00, 2)
        if len(raw) != 2:
            raise ValueError("Incomplete TMP117 sample")
        value = (raw[0] << 8) | raw[1]
        if value & 0x8000:
            value -= 65536
        temperature = value / 128.0
        if not -40 <= temperature <= 125:
            raise ValueError("TMP117 sample outside supported range")
        return temperature
