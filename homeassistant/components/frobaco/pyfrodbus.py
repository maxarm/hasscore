"""FroniusModbusTCP allows connection and interaction with a Fronius inverter using Modbus TCP."""

from pyModbusTCP import utils
from pyModbusTCP.client import ModbusClient

from homeassistant.helpers.typing import StateType

# Format:
# "name : [register address, data type, unit 1]
registers = {
    "CommonBlockRegister": {
        "SunspecSID": [40001, "uint32", 1],
        "SunspecID": [40070, "uint16", 1],
        "AC_Phase-A_Current": [40072, "float", 1],
        "AC_Phase-B_Current": [40076, "float", 1],
        "AC_Phase-C_Current": [40078, "float", 1],
        "AC_Voltage_Phase-AB": [40080, "float", 1],
        "AC_Voltage_Phase-BC": [40082, "float", 1],
        "AC_Voltage_Phase-CA": [40084, "float", 1],
        "AC_Voltage_Phase-A-N": [40086, "float", 1],
        "AC_Voltage_Phase-B-N": [40088, "float", 1],
        "AC_Voltage_Phase-C-N": [40090, "float", 1],
        "AC_Output_Power": [40092, "float", 1],
        "AC_Frequency": [40094, "float", 1],
        "DC_Power": [40101, "uint16", 1],
        "AC_Power": [40088, "uint16", 1],
        "Cabinet_Temperature": [40110, "float", 1],
        "InOutWRte_RvrtTms_Fallback": [40359, "uint16", 1],
        "Operating_State": [40118, "uint16", 1],
    },
    "StorageDevice": {
        "Battery_capa": [40141, "uint16", 1],
        "Battery_DC_Power_in": [40315, "uint16", 1],
        "Battery_DC_Power_out": [40335, "uint16", 1],
        "Battery_SunspecID": [40344, "uint16", 1],
        "Battery_MinRsvPct": [40351, "uint16", 1],
        "Battery_SoC": [40352, "uint16", 1],
        "Battery_Status": [40355, "uint16", 1],
        "battery_charge_rate": [40346, "uint16", 1],
        "battery_max_discharge_percent": [40356, "uint16", 1],
        "battery_max_charge_percent": [40357, "uint16", 1],
        "storage_control_mode": [
            40349,
            "uint16",
            1,
        ],  # bitfield16 eigentlich, wird aber nicht abgefangen
    },
    "MultipleMPPT": {
        "MPPT_SunspecID": [40254, "uint16", 1],
        "MPPT_Current_Scale_Factor": [40256, "uint16", 1],
        "MPPT_Voltage_Scale_Factor": [40257, "uint16", 1],
        "MPPT_Power_Scale_Factor": [40258, "uint16", 1],
        "MPPT_1_DC_Current": [40273, "uint16", 1],
        "MPPT_1_DC_Voltage": [40274, "uint16", 1],
        "MPPT_1_DC_Power": [40275, "uint16", 1],
        "MPPT_1_Temperature": [40280, "uint16", 1],
        "MPPT_1_State": [40281, "uint16", 1],
        "MPPT_2_DC_Current": [40293, "uint16", 1],
        "MPPT_2_DC_Voltage": [40294, "uint16", 1],
        "MPPT_2_DC_Power": [40295, "uint16", 1],
        "MPPT_2_Temperature": [40300, "uint16", 1],
        "MPPT_2_State": [40301, "uint16", 1],
    },
    "PowerMeter": {
        "Meter_SunspecID": [40070, "uint16", 200],
        "Meter_Frequency": [40086, "uint16", 200],
        "Meter_Power_Total": [40088, "uint16", 200],
        "Meter_Power_L1": [40089, "uint16", 200],
        "Meter_Power_L2": [40090, "uint16", 200],
        "Meter_Power_L3": [40091, "uint16", 200],
        "Meter_Power_Scale_Factor": [40092, "uint16", 200],
    },
}


class Sensor:
    """pyfrodbus sensor."""

    def __init__(self, name: str, state: StateType = None) -> None:  # noqa: D107
        self._name = name
        self._state = state

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self) -> StateType:
        """Return the state of the sensor."""
        return self._state

    @state.setter
    def state(self, state: StateType):
        self._state = state


class FroniusModbusTcp:
    """FroniusModbusTCP type."""

    def __init__(self, host, port, auto=True) -> None:
        """Initialize the FroniusModbusTCP type."""
        self._modbus = ModbusClient(
            host=host, port=port, auto_open=True, auto_close=True, debug=False
        )

    async def device_info(self) -> dict:
        """Simulate device info and return the results."""
        return {"serial": "9137319fro"}

    def get_sensors(self) -> list[Sensor]:
        """Provide a list of available sensors."""
        sensors: list[Sensor] = list[Sensor]()

        sensors.append(Sensor("storage_control_mode"))
        sensors.append(Sensor("battery_charge_rate"))
        sensors.append(Sensor("battery_max_discharge_percent"))
        sensors.append(Sensor("battery_max_charge_percent"))

        return sensors

    async def read(self, sensors: list[Sensor]) -> bool:
        """Read a set of keys.

        Returns:
            bool: reading was successful

        """

        for sensor in sensors:
            if sensor.name in (
                "battery_max_discharge_percent",
                "battery_max_charge_percent",
            ):
                value = self.read_data(sensor.name)
                value = utils.get_2comp(int(value))
                value /= 100
                sensor.state = value

            else:
                sensor.state = self.read_data(sensor.name)

        return True

    def read_uint16(self, addr):  # noqa: D102
        regs = self._modbus.read_holding_registers(addr - 1, 1)
        if regs:
            return int(regs[0])
        return False

    def read_uint32(self, addr):  # noqa: D102
        regs = self._modbus.read_holding_registers(addr - 1, 2)
        if regs:
            return int(utils.word_list_to_long(regs, big_endian=True)[0])
        return False

    def read_float(self, addr):  # noqa: D102
        regs = self._modbus.read_holding_registers(addr - 1, 2)
        if not regs:
            return False

        list_32_bits = utils.word_list_to_long(regs, big_endian=True)
        return float(utils.decode_ieee(list_32_bits[0]))

    def read_data(self, parameter: str):  # noqa: D102
        sectionMatch = None
        for section, properties in registers.items():
            for key in properties:
                if key == parameter:
                    sectionMatch = section

        if sectionMatch is None:
            raise Exception  # noqa: TRY002

        [register, datatype, unit_id] = registers[sectionMatch][parameter]

        self._modbus.unit_id = unit_id
        if datatype == "float":
            return self.read_float(register)
        if datatype == "uint32":
            return self.read_uint32(register)
        if datatype == "uint16":
            return self.read_uint16(register)
        return False
