import math
from typing import Final, Tuple
from tank import OxidizerTank


class GenericOxidizer:
    """
    GenericOxidizer - Overridable class that can be used to define various Oxidizers
    and their properties.

    This is the generic equivalent to "NOX.m" in the MATLAB code
    """
    SPECIFIC_HEAT_RATIO: float          = 0
    GAS_CONSTANT: float                 = 0
    Pc: float                           = 0
    Tc: float                           = 0
    rhoc: float                         = 0
    R: float                            = 0
    VAPOR_PRESSURE_EXPONENTS: list      = []
    LIQUID_DENSITY_EXPONENTS: list      = []
    VAPOR_DENSITY_EXPONENTS: list       = []
    LIQUID_ENTHALPY_EXPONENTS: list     = []
    VAPOR_ENTHALPY_EXPONENTS: list      = []
    SPECIFIC_HEAT_CAPACITY_EXPONENTS: list = []

    def get_specific_heat_ratio(self) -> float:
        """

        :return:
        """
        return self.SPECIFIC_HEAT_RATIO

    def get_vapor_pressure(self, tank:OxidizerTank) -> float:
        """

        :param tank:
        :return:
        """
        return self.Pc * math.exp(
            (1/(tank.get_temperature() / self.Tc)) * (
                    self.VAPOR_PRESSURE_EXPONENTS[0] * (1 - tank.get_temperature() / self.Tc) +
                    self.VAPOR_PRESSURE_EXPONENTS[1] * math.pow(1 - tank.get_temperature() / self.Tc, 3/2) +
                    self.VAPOR_PRESSURE_EXPONENTS[2] * math.pow(1 - tank.get_temperature() / self.Tc, 5/2) +
                    self.VAPOR_PRESSURE_EXPONENTS[1] * math.pow(1 - tank.get_temperature() / self.Tc, 5)
            )
        )

    def get_saturated_density(self, tank:OxidizerTank) -> Tuple[float, float]:
        """

        :param tank:
        :return: Tuple(Liquid Density, Vapor Density)
        """
        liquid_density = self.rhoc * math.exp(
            self.LIQUID_DENSITY_EXPONENTS[0] * math.pow(1 - (tank.get_temperature() / self.Tc), 1/3) +
            self.LIQUID_DENSITY_EXPONENTS[1] * math.pow(1 - (tank.get_temperature() / self.Tc), 2/3) +
            self.LIQUID_DENSITY_EXPONENTS[2] * (1 - (tank.get_temperature() / self.Tc)) +
            self.LIQUID_DENSITY_EXPONENTS[0] * math.pow(1 - (tank.get_temperature() / self.Tc), 4/3)
        )

        vapor_density = self.rhoc * math.exp(
            self.VAPOR_DENSITY_EXPONENTS[0] * math.pow(self.Tc / tank.get_temperature() - 1, 1/3) +
            self.VAPOR_DENSITY_EXPONENTS[1] * math.pow(self.Tc / tank.get_temperature() - 1, 2/3) +
            self.VAPOR_DENSITY_EXPONENTS[2] * (self.Tc / tank.get_temperature() - 1) +
            self.VAPOR_DENSITY_EXPONENTS[3] * math.pow(self.Tc / tank.get_temperature() - 1, 4/3) +
            self.VAPOR_DENSITY_EXPONENTS[4] * math.pow(self.Tc / tank.get_temperature() - 1, 5/3)
        )

        return liquid_density, vapor_density

    def get_heat_of_vaporization(self, tank:OxidizerTank) -> float:
        """

        :param tank:
        :return:
        """
        return ((self.LIQUID_ENTHALPY_EXPONENTS[0] - self.VAPOR_ENTHALPY_EXPONENTS[0])
            (self.LIQUID_ENTHALPY_EXPONENTS[1] - self.VAPOR_ENTHALPY_EXPONENTS[1]) * math.pow(1-(tank.get_temperature() / self.Tc), 1/3) +
            (self.LIQUID_ENTHALPY_EXPONENTS[2] - self.VAPOR_ENTHALPY_EXPONENTS[2]) * math.pow(1-(tank.get_temperature() / self.Tc), 2/3) +
            (self.LIQUID_ENTHALPY_EXPONENTS[3] - self.VAPOR_ENTHALPY_EXPONENTS[3]) * (1-(tank.get_temperature() / self.Tc)) +
            (self.LIQUID_ENTHALPY_EXPONENTS[4] - self.VAPOR_ENTHALPY_EXPONENTS[4]) * math.pow(1-(tank.get_temperature() / self.Tc), 4/3)
        )

    def get_specific_heat_capacity(self, tank:OxidizerTank) -> float:
        """

        :param tank:
        :return:
        """
        return self.SPECIFIC_HEAT_CAPACITY_EXPONENTS[0] * (
                1 + self.SPECIFIC_HEAT_CAPACITY_EXPONENTS[1] * math.pow(1-(tank.get_temperature() / self.Tc), -1) +
                self.SPECIFIC_HEAT_CAPACITY_EXPONENTS[2] * (1-(tank.get_temperature() / self.Tc)) +
                self.SPECIFIC_HEAT_CAPACITY_EXPONENTS[3] * math.pow(1-(tank.get_temperature() / self.Tc), 2) +
                self.SPECIFIC_HEAT_CAPACITY_EXPONENTS[4] * math.pow(1-(tank.get_temperature() / self.Tc), 3)
        )

    def get_saturated_vapor_compressibility_factor(self, tank:OxidizerTank) -> float:
        """

        :param tank:
        :return:
        """
        # op.Z = (Pc*exp((1/(T/Tc))*(a1*(1-T/Tc) + ...
        #     a2*(1-(T/Tc))^(3/2) + a3*(1-(T/Tc))^(5/2) + a4*(1-(T/Tc))^5)))/ ...
        #     ((rhoc*exp(c1*((Tc/T)-1)^(1/3) + c2*((Tc/T)-1)^(2/3) + c3*((Tc/T)-1)...
        #     + c4*((Tc/T)-1)^(4/3) + c5*((Tc/T)-1)^(5/3)))*R*T);
        # It seems like there is a lot of redundant calculations in the above
        # that equate to the following:
        return self.get_vapor_pressure(tank) / self.get_saturated_density(tank)[1]

class NOXOxidizer(GenericOxidizer):
    """
    Properties of NOX as an oxidizer
    Gathered through empirical evidence according to NOX.m
    """
    SPECIFIC_HEAT_RATIO: Final[float]           = 1.31
    GAS_CONSTANT: Final[float]                  = 188.91
    Pc: Final[float]                            = 7251000.0
    Tc: Final[float]                            = 309.57
    rhoc: Final[float]                          = 452.0
    R: Final[float]                             = 188.91
    VAPOR_PRESSURE_EXPONENTS: Final[list]       = [-6.71893, 1.35966, -1.3779, -4.051]
    LIQUID_DENSITY_EXPONENTS: Final[list]       = [1.72328, -0.83950, 0.51060, -0.10412]
    VAPOR_DENSITY_EXPONENTS: Final[list]        = [-1.00900, -6.28792, 7.50332, -7.90463, 0.629427]
    LIQUID_ENTHALPY_EXPONENTS: Final[list]      = [-200, 116.043, -917.225, 794.779, -589.587]
    VAPOR_ENTHALPY_EXPONENTS: Final[list]       = [-200, 440.055, -459.701, 434.081, -485.338]
    SPECIFIC_HEAT_CAPACITY_EXPONENTS: Final[list] = [2.49973, 0.023454, -3.80136, 13.0945, -14.5180]

    def __init__(self):
        super().__init__()


