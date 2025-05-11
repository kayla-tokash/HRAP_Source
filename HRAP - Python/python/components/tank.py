import math
from typing import Tuple, Final
from ..simulation.simulation import Simulation, SimulationState
from motor import MotorProperties
import oxidizer

class OxidizerTank:
    tank_volume = 0
    mass_discharged_rate = 0

    # Currently we only support NOX
    oxidizer = Final[oxidizer.NOXOxidizer()]

    def __init__(self, volume:float):
        self.tank_volume = Final[float](volume)

    def get_tank_volume(self):
        return self.tank_volume

    def get_pressure_change(self, state:SimulationState) -> float:
        """
        Get the change in pressure in the tank
        :param state:
        :return:
        """
        # dP = x.P_tnk - x.P_cmbr;
        # if dP < 0
        #     dP = 0;
        # end
        return max(0.0, state.get_tank_pressure() - state.get_chamber_pressure())

    def get_mass_combustion_chamber(self, state:SimulationState) -> float:
        """
        Get mass in the combustion chamber
        :param state:
        :return:
        """
        # Mcc = sqrt(x.ox_props.Z * 1.31 * 188.91 * x.T_tnk * (x.P_cmbr / x.P_tnk) ^ (0.31 / 1.31));
        # z = state.get_oxidizer().get_saturated_vapor_compressibility_factor(self)
        # 1.31 is the specific heat ratio of nitrous oxide and 188.91 is the gas constant for nitrous. The 0.31 is just 1.31-1 or gamma-1 which is a fairly common term in the thermo models, 2.31 is the same just gamma+1. 0.62 is I believe 2*gamma-2.
        m_cc = math.sqrt(self.get_oxidizer().get_saturated_vapor_compressibility_factor(self) *
             self.get_oxidizer().SPECIFIC_HEAT_RATIO * self.get_oxidizer().GAS_CONSTANT *
             self.get_temperature(state) * math.pow(
                state.get_chamber_pressure() / self.get_tank_pressure(state),
                (self.get_oxidizer().SPECIFIC_HEAT_RATIO - 1) / self.get_oxidizer().SPECIFIC_HEAT_RATIO
             )
        )
        # if Mcc >= 1
        #     Mcc = 1;
        # end
        #
        return min(1.0, m_cc)

    def get_tank_pressure(self, state:SimulationState):
        return state.get_tank_pressure()


# not sure about this one
    def get_mass_atmosphere(self, simulation:Simulation, state:SimulationState) -> float:
        """
        Get mass discharged into the atmosphere?
        :param simulation:
        :param state:
        :return:
        """
        # if Matm >= 1
        #     Matm = 1;
        # end
        # Matm = sqrt(x.ox_props.Z * 1.31 * 188.91 * x.T_tnk * (s.Pa / x.P_tnk) ^ (0.31 / 1.31));
        m_atm = math.sqrt(self.get_oxidizer().get_saturated_vapor_compressibility_factor(self) *
             self.get_oxidizer().SPECIFIC_HEAT_RATIO * self.get_oxidizer().GAS_CONSTANT *
             self.get_temperature(state) * math.pow(
                state.get_atmospheric_pressure() / self.get_tank_pressure(state),
                (self.get_oxidizer().SPECIFIC_HEAT_RATIO - 1) / self.get_oxidizer().SPECIFIC_HEAT_RATIO
             )
        )
        return min(1.0, m_atm)

    def set_mass_discharge_rate(self, mass:float):
        """
        Setter for mass discharge rate
        :param mass:
        :return:
        """
        self.mass_discharged_rate = mass

    def get_mass_discharge_rate(self) -> float:
        """
        Getter for mass discharge rate
        :return:
        """
        return self.mass_discharged_rate

    # need more context about what each vent state is
    def get_vent_state(self, simulation:Simulation) -> int:
        return simulation.get_vent_state() #simulation.vent_state [0,1,2]

    # mdot? # mD?
    def update_mass_flow_and_discharge_rates(self, simulation:Simulation, state:SimulationState, motor:MotorProperties):
        # if s.tburn == 0 | | t <= s.tburn
        if motor.get_burn_time() == 0 or not simulation.is_time_maxed():
            # if s.vnt_S == 0
            if self.get_vent_state(simulation) == simulation.VENT_STATE_ZERO:
                # x.mdot_v = 0;
                state.set_mass_flow_rate_vent(0)
                # if x.mLiq_new == 0
                #     x.mdot_o = (s.inj_CdA * s.inj_N * x.P_tnk / sqrt(x.T_tnk)) * sqrt(
                #         1.31 / (x.ox_props.Z * 188.91)) * Mcc * (1 + (0.31) / 2 * Mcc ^ 2) ^ (-2.31 / 0.62);
                # else
                #     x.mdot_o = s.inj_CdA * s.inj_N * sqrt(2 * x.ox_props.rho_l * dP);
                # end
                if state.get_mass_liquid_new() == 0:
                    state.set_mass_flow_output(0) # TODO write the math lol
                else:
                    state.set_mass_flow_output(0) # TODO write the math lol
                self.set_mass_discharge_rate((state.get_mass_flow_output() + state.get_mass_flow_vent()) * simulation.get_time_delta())
            elif self.get_vent_state(simulation) == simulation.VENT_STATE_ONE:
                # # 1.31 is the specific heat ratio of nitrous oxide and 188.91 is the gas constant for nitrous. The 0.31 is just 1.31-1 or gamma-1 which is a fairly common term in the thermo models, 2.31 is the same just gamma+1. 0.62 is I believe 2*gamma-2.
                # x.mdot_v = (s.vnt_CdA * x.P_tnk / sqrt(x.T_tnk)) * sqrt(1.31 / (x.ox_props.Z * 188.91)) * Matm * (
                #             1 + (0.31) / 2 * Matm ^ 2) ^ (-2.31 / 0.62);
                state.set_mass_flow_rate_vent(0) #TODO add the math
                # if x.mLiq_new == 0
                #     x.mdot_o = (s.inj_CdA * s.inj_N * x.P_tnk / sqrt(x.T_tnk)) * sqrt(
                #         1.31 / (x.ox_props.Z * 188.91)) * Mcc * (1 + (0.31) / 2 * Mcc ^ 2) ^ (-2.31 / 0.62);
                # else
                #     x.mdot_o = s.inj_CdA * s.inj_N * sqrt(2 * x.ox_props.rho_l * dP);
                # end
                if state.get_mass_liquid_new() == 0:
                    state.set_mass_flow_output(0)  # TODO write the math lol
                else:
                    state.set_mass_flow_output(0)  # TODO write the math lol
                # mD = (x.mdot_o + x.mdot_v) * dt;
                self.set_mass_discharge_rate((state.get_mass_flow_output() + state.get_mass_flow_vent()) * simulation.get_time_delta())
            elif self.get_vent_state(simulation) == simulation.VENT_STATE_TWO:
                # x.mdot_v = (s.vnt_CdA * x.P_tnk / sqrt(x.T_tnk)) * sqrt(1.31 / (x.ox_props.Z * 188.91)) * Matm * (
                #                     1 + (0.31) / 2 * Matm ^ 2) ^ (-2.31 / 0.62);
                state.set_mass_flow_rate_vent(0) # TODO add the math
                #         if x.mLiq_new == 0
                #             x.mdot_o = (s.inj_CdA * s.inj_N * x.P_tnk / sqrt(x.T_tnk)) * sqrt(1.31 / (x.ox_props.Z * 188.91)) * Mcc * (
                #                         1 + (0.31) / 2 * Mcc ^ 2) ^ (-2.31 / 0.62);
                #         else
                #             x.mdot_o = s.inj_CdA * s.inj_N * sqrt(2 * x.ox_props.rho_l * dP) + x.mdot_v;
                #         end
                if state.get_mass_liquid_new() == 0:
                    state.set_mass_flow_output(0)  # TODO write the math lol
                else:
                    state.set_mass_flow_output(0)  # TODO write the math lol
                #         mD = x.mdot_o * dt;
                self.set_mass_discharge_rate((state.get_mass_flow_output() + state.get_mass_flow_vent()) * simulation.get_time_delta())
            else:
                raise RuntimeError(f"Invalid vent state [{self.get_vent_state(simulation)}]")
        else:
            # x.mdot_o = 0;
            # mD = 0;
            state.set_mass_flow_output(0)
            self.set_mass_discharge_rate(0)

    def get_mass_discharged(self, simulation:Simulation, state:SimulationState) -> Tuple[float, float]:
        """
        Mass discharged from the motor
        m_o_old = x.m_o;
        x.m_o = x.m_o - x.mdot_o * dt;
        :param simulation: Static information about the simulation
        :param state: Current and past state of the iteration for the sim
        :return: Tuple(previous value of mass discharged, current value of mass discharged)
        """

        mass_discharged_old = state.get_mass_discharged()
        state.set_mass_discharged((state.get_mass_discharged() - state.get_mass_discharge_flow()) * simulation.get_time_delta())
        return mass_discharged_old, state.get_mass_discharged()  # (m_out_old, mass out new)

    # TODO I need to figure out what is being given by tank.m
    # It looks like LNOX evaporation information

    """
if x.mLiq_new < x.mLiq_old && x.mLiq_new > 0 && x.mdot_o > 0

    %Find mass of liquid nitrous evaporated during time step
        x.mLiq_old = x.mLiq_new - mD;
        [x.ox_props] = NOX(x.T_tnk);
        x.mLiq_new = (s.tnk_V - (x.m_o/x.ox_props.rho_v))/ ...
                    ((1/x.ox_props.rho_l)-(1/x.ox_props.rho_v));
        mv = x.mLiq_old - x.mLiq_new;

    %Find heat removed from liquid
        dT = -mv*x.ox_props.Hv/(x.mLiq_new*x.ox_props.Cp);
        x.T_tnk = x.T_tnk + dT;
        [op] = NOX(x.T_tnk);
        x.dP = op.Pv - x.P_tnk;

elseif x.mLiq_new >= x.mLiq_old && x.mLiq_new > 0 && x.mdot_o > 0
    
    dP_avg = mean(o.dP(1:sum(o.dP<0)));

    P_new = x.P_tnk + dP_avg;

    vp = @(T) 7251000*exp((1/(T/309.57))*...
        (-6.71893*(1-T/309.57) + 1.35966*(1-(T/309.57))^(3/2) + -1.3779*...
        (1-(T/309.57))^(5/2) + -4.051*(1-(T/309.57))^5)) - P_new;

    x.T_tnk = fzero(vp,x.T_tnk);

    x.dP = x.ox_props.Pv - x.P_tnk;

    [x.ox_props] = NOX(x.T_tnk);

    x.mLiq_new = (s.tnk_V - (x.m_o/x.ox_props.rho_v))/ ...
                    ((1/x.ox_props.rho_l)-(1/x.ox_props.rho_v));
    x.mLiq_old = 0;

elseif x.mLiq_new <= 0 && x.mdot_o > 0
    
    if x.mLiq_new ~= 0
        x.mLiq_new = 0;
    end

    %Find Z factor

    Z_old = x.ox_props.Z;

    Zguess = Z_old;
    epsilon = 1;
    
    Ti = x.T_tnk;
    Pi = x.P_tnk;

    while epsilon >= 0.000001

        T_ratio = ((Zguess*x.m_o)/(Z_old*m_o_old))^(0.3);
        x.T_tnk = T_ratio*Ti;
        P_ratio = T_ratio^(1.3/0.3);
        x.P_tnk = P_ratio*Pi;

        [x.ox_props] = NOX(x.T_tnk);

        Z = x.ox_props.Z;
        
        epsilon = abs(Zguess - Z);

        Zguess = (Zguess + Z)/2;

    end
    
end
"""

    def get_temperature(self, state:SimulationState):
        return state.get_tank_temperature()

    def get_oxidizer(self):
        return self.oxidizer