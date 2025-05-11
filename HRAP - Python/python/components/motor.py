
from ..components.tank import OxidizerTank

class MotorProperties:
    tank = None

    def __init__(self, tank:OxidizerTank):
        pass

    def get_grain_outer_diameter(self) -> float:
        # TODO Add a class variable for this
        return 0

    def get_burn_time(self) -> float:
        return 0
