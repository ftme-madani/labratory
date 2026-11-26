from dataclasses import dataclass

@dataclass
class CircuitPhysicsState:
    battery_voltage_volts: float = 1.5
    bulb_resistance_ohms: float = 10.0
    ammeter_resistance_ohms: float = 0.05
    wire_resistance_ohms: float = 0.05
    is_switch_closed: bool = False
    is_loop_connected: bool = False
    has_ammeter: bool = False
    has_bulb: bool = True
    has_battery: bool = True

    @property
    def total_resistance_ohms(self) -> float:
        r = self.wire_resistance_ohms
        if self.has_bulb:
            r += self.bulb_resistance_ohms
        if self.has_ammeter:
            r += self.ammeter_resistance_ohms
        return max(r, 0.01)

    @property
    def is_short_circuit(self) -> bool:
        # اتصال دو سر باتری بدون مقاومت مصرف‌کننده (لامپ)
        return self.is_loop_connected and self.is_switch_closed and not self.has_bulb

    @property
    def current_amperes(self) -> float:
        if not self.is_loop_connected or not self.is_switch_closed:
            return 0.0
        if self.is_short_circuit:
            return 999.0  # جریان اضافه بار و اتصال کوتاه
        return round(self.battery_voltage_volts / self.total_resistance_ohms, 3)

    @property
    def bulb_power_watts(self) -> float:
        if not self.is_loop_connected or not self.is_switch_closed or not self.has_bulb:
            return 0.0
        i = self.current_amperes
        return round((i ** 2) * self.bulb_resistance_ohms, 3)

    @property
    def is_bulb_lit(self) -> bool:
        return self.bulb_power_watts >= 0.05
