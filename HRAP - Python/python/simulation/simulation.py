
from ..components.sim_config import SimulationConfiguration
from ..components.motor import MotorProperties
from typing import Final

class Simulation:
    """
    Simulation()
    Provides interfaces with the simulation for looping, iterating, and loading config
    """

    config = None
    motor_properties = None

    i = 0
    time = 0
    end_condition = None

    # TODO find where these are defined in the matlab code and get more context about their variable names
    inj_CdA = 0
    inj_N = 0

    def __init__(self, config:SimulationConfiguration, motor_properties:MotorProperties):
        self.set_simulation_config(config)
        self.set_motor_properties(motor_properties)

    # Loop for the simulation

    def loop(self):
        """
        loop()
        Run the simulation loop until it reaches an end condition
        """
        while self.end_condition is None:
            # Iterate the time frame
            self.i += 1
            self.time += self.get_time_delta()

            # Evaluate the data for that iteration
            self.run_iteration(self.get_current_time(), self.i)

            # Check if the simulation has ended
            if self.is_fuel_depleted():
                self.end_condition = "Fuel Depleted"
            if self.is_oxidizer_depleted():
                self.end_condition = "Oxidizer Depleted"
            if self.is_time_maxed():
                self.end_condition = "Max Simulation Time Reached"
            if self.is_burn_complete():
                self.end_condition = "Burn Completed"

    def run_iteration(self, t:float, i:int):
        """
        iterate_sim(...)
        Steps the simulation one iteration of time t
        :param t: time
        :param i: iteration
        :return:
        """
        pass

    # Simulations checks

    def is_fuel_depleted(self):
        # TODO check if the inner diameter of the grain is greater than the outer diameter
        return False

    def is_oxidizer_depleted(self):
        # TODO check if the mass of the tank is <= 0
        return False

    def is_time_maxed(self):
        # TODO check if the time has exceeded the max sim time
        return False

    def is_burn_complete(self):
        # TODO check if the pressure in the chamber is greater
        # than the atmospheric pressure
        return False

    # Getters and Setters

    def set_motor_properties(self, motor_properties:MotorProperties):
        # TODO Do any checks
        self.motor_properties = motor_properties

    def get_motor_properties(self) -> MotorProperties:
        return self.motor_properties

    def set_simulation_config(self, config:SimulationConfiguration):
        # TODO Do any checks
        self.config = config

    def get_simulation_config(self) -> SimulationConfiguration:
        return self.config

    def get_time_delta(self) -> float:
        # TODO get this from the config
        return 0

    def get_current_time(self) -> float:
        return self.time

    def set_vent_state(self, vent_state:int):
        self.vent_state = vent_state


class SimulationState:
    """
    Holds the state of each iteration in the sim (basically 'x' from the matlab code)
    """
    class VentState:
        # Todo: get more information about what each vent state represents in context
        VENT_STATE_ZERO:Final[int] = 0
        VENT_STATE_ONE:Final[int] = 1
        VENT_STATE_TWO:Final[int] = 2
        VENT_STATE_UNKNOWN:Final[int] = -1

    vent_state = VentState.VENT_STATE_UNKNOWN

    def get_vent_state(self) -> int:
        return self.vent_state

    def set_vent_state(self, state:int):
        self.vent_state = state

    def get_mass_discharged(self) -> float:
        return 0

    def set_mass_discharged(self, mass_discharged:float):
        pass

    def get_mass_discharge_flow(self) -> float:
        return 0

    def set_mass_flow_rate_vent(self, float_rate:float):
        pass

    def get_mass_liquid_new(self): # TODO figure out return type
        return 0

    def set_mass_flow_output(self, flow_rate:float):
        pass

    def get_mass_flow_output(self) -> float:
        return 0

    def get_mass_flow_vent(self) -> float:
        return 0

    def get_tank_pressure(self) -> float:
        return 0

    def get_chamber_pressure(self) -> float:
        return 0

    def get_tank_temperature(self) -> float:
        return 0

    def get_atmospheric_pressure(self) -> float:
        return 0



