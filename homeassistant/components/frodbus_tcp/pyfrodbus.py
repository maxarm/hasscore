"""FroniusModbusTCP allows connection and interaction with a Fronius inverter using Modbus TCP."""


class FroniusModbusTcp:
    """FroniusModbusTCP type."""

    def __init__(self, host, port, auto=True) -> None:
        """Initialize the FroniusModbusTCP type."""
        return

    async def device_info(self) -> dict:
        """Simulate device info and return the results."""
        return {"serial": "9137319fro"}

    async def read(self) -> bool:
        """Read a set of keys.

        Returns:
            bool: reading was successful

        """
        return True
