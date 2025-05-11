import math
from typing import Final
from tank import OxidizerTank
from ..simulation.simulation import SimulationState


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

    # Curve information about the oxidizer
    VAPOR_PRESSURE_COEFFICIENTS: list           = []
    LIQUID_DENSITY_COEFFICIENTS: list           = []
    VAPOR_DENSITY_COEFFICIENTS: list            = []
    LIQUID_ENTHALPY_COEFFICIENTS: list          = []
    VAPOR_ENTHALPY_COEFFICIENTS: list           = []
    SPECIFIC_HEAT_CAPACITY_COEFFICIENTS: list   = []
    VAPOR_PRESSURE_EXPONENTS: list               = []
    LIQUID_DENSITY_EXPONENTS: list               = []
    VAPOR_DENSITY_EXPONENTS: list                = []
    ENTHALPY_EXPONENTS: list                     = []
    SPECIFIC_HEAT_CAPACITY_EXPONENTS: list       = []

    def get_specific_heat_ratio(self) -> float:
        """
        Get the specific heat ratio of the oxidizer
        :return: float
        """
        return self.SPECIFIC_HEAT_RATIO

    def get_vapor_pressure(self, tank:OxidizerTank, state:SimulationState) -> float:
        """
        Get the current vapor pressure of the oxidizer in the tank
        :param tank: Oxidizer tank properties
        :param state: Recorded simulation state
        :return: float
        """
        assert len(self.VAPOR_PRESSURE_COEFFICIENTS) == len(self.VAPOR_PRESSURE_EXPONENTS)
        return self.Pc * math.exp(
            (1 / (tank.get_temperature(state) / self.Tc)) * (
                sum(self.VAPOR_PRESSURE_COEFFICIENTS[index] *
                    math.pow(1 - tank.get_temperature(state) / self.Tc, self.VAPOR_PRESSURE_EXPONENTS[index])
                    for index in range(len(self.VAPOR_PRESSURE_COEFFICIENTS)))
            )
        )

    def get_saturated_density_liquid(self, tank:OxidizerTank, state:SimulationState) -> float:
        """
        Get the current liquid pressure of the oxidizer in the tank
        :param tank: Oxidizer tank properties
        :param state: Recorded simulation state
        :return: float
        """
        assert len(self.LIQUID_DENSITY_COEFFICIENTS) == len(self.LIQUID_DENSITY_EXPONENTS)
        return self.rhoc * math.exp(
            sum(self.LIQUID_DENSITY_COEFFICIENTS[index] *
                math.pow(1 - (tank.get_temperature(state) / self.Tc), self.LIQUID_DENSITY_EXPONENTS[index])
                for index in range(len(self.LIQUID_DENSITY_COEFFICIENTS)))
        )

    def get_saturated_density_vapor(self, tank:OxidizerTank, state:SimulationState) -> float:
        """
        Get the saturated density of the oxidizer in vapor state
        :param tank: Oxidizer tank properties
        :param state: Recorded simulation state
        :return: float
        """
        assert len(self.VAPOR_DENSITY_COEFFICIENTS) == len(self.VAPOR_DENSITY_EXPONENTS)
        return self.rhoc * math.exp(
            sum(self.VAPOR_DENSITY_COEFFICIENTS[index] *
                math.pow(self.Tc / tank.get_temperature(state) - 1, self.VAPOR_DENSITY_EXPONENTS[index])
                for index in range(len(self.VAPOR_DENSITY_COEFFICIENTS)))
        )

    def get_heat_of_vaporization(self, tank:OxidizerTank, state:SimulationState) -> float:
        """
        Get the heat of vaporization of the oxidizer
        :param tank: Oxidizer tank properties
        :param state: Recorded simulation state
        :return: float
        """
        assert len(self.LIQUID_ENTHALPY_COEFFICIENTS) == len(self.VAPOR_ENTHALPY_COEFFICIENTS)
        assert len(self.LIQUID_ENTHALPY_COEFFICIENTS) == len(self.ENTHALPY_EXPONENTS)
        return sum((self.LIQUID_ENTHALPY_COEFFICIENTS[index] - self.VAPOR_ENTHALPY_COEFFICIENTS[index]) *
                math.pow(1 - (tank.get_temperature(state) / self.Tc), self.ENTHALPY_EXPONENTS[index])
                   for index in range(len(self.LIQUID_ENTHALPY_COEFFICIENTS))
        )

    def get_specific_heat_capacity(self, tank:OxidizerTank, state:SimulationState) -> float:
        """
        Get the specific heat capacity of the oxidizer
        :param tank: Oxidizer tank properties
        :param state: Recorded simulation state
        :return: float
        """
        assert len(self.SPECIFIC_HEAT_CAPACITY_COEFFICIENTS) > 1
        assert len(self.SPECIFIC_HEAT_CAPACITY_COEFFICIENTS) == len(self.SPECIFIC_HEAT_CAPACITY_EXPONENTS) + 1
        return self.SPECIFIC_HEAT_CAPACITY_COEFFICIENTS[0] * (1 +
            sum(self.SPECIFIC_HEAT_CAPACITY_COEFFICIENTS[index + 1] *
                math.pow(1 - (tank.get_temperature(state) / self.Tc), self.SPECIFIC_HEAT_CAPACITY_EXPONENTS[index]))
                for index in range(len(self.SPECIFIC_HEAT_CAPACITY_EXPONENTS))
        )

    def get_saturated_vapor_compressibility_factor(self, tank:OxidizerTank, state:SimulationState) -> float:
        """
        Get the saturated vapor compressibility factor
        :param tank: Oxidizer tank properties
        :param state: Recorded simulation state
        :return: float
        """
        # It seems like there is a lot of redundant calculations in the "NOX.m" calculation
        # that equate to the following:
        return self.get_vapor_pressure(tank, state) / self.get_saturated_density_vapor(tank, state)


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
    VAPOR_PRESSURE_COEFFICIENTS: Final[list]            = [-6.71893, 1.35966, -1.3779, -4.051]
    LIQUID_DENSITY_COEFFICIENTS: Final[list]            = [1.72328, -0.83950, 0.51060, -0.10412]
    VAPOR_DENSITY_COEFFICIENTS: Final[list]             = [-1.00900, -6.28792, 7.50332, -7.90463, 0.629427]
    LIQUID_ENTHALPY_COEFFICIENTS: Final[list]           = [-200, 116.043, -917.225, 794.779, -589.587]
    VAPOR_ENTHALPY_COEFFICIENTS: Final[list]            = [-200, 440.055, -459.701, 434.081, -485.338]
    SPECIFIC_HEAT_CAPACITY_COEFFICIENTS: Final[list]    = [2.49973, 0.023454, -3.80136, 13.0945, -14.5180]
    VAPOR_PRESSURE_EXPONENTS: Final[list]               = [1.0, 3/2, 5/2, 5]
    LIQUID_DENSITY_EXPONENTS: Final[list]               = [1/3, 2/3, 1.0, 4/3]
    VAPOR_DENSITY_EXPONENTS: Final[list]                = [1/3, 2/3, 1.0, 4/3, 5/3]
    ENTHALPY_EXPONENTS: Final[list]                     = [0, 1/3, 2/3, 1.0, 4/3]
    SPECIFIC_HEAT_CAPACITY_EXPONENTS: Final[list]       = [-1.0, 1.0, 2.0, 3.0]

    def __init__(self):
        super().__init__()


