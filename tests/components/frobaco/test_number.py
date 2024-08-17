"""Tests for our Number types."""

# async def test_BatteryChargePowerNumber(  # noqa: D103
#     hass: HomeAssistant,
# ) -> None:
#     BatteryMaxChargePowerNumber(
#         hass,
#     )

#     config_entry = await setup_frobaco_integration(hass)

#     assert len(hass.states.async_all(domain_filter=SENSOR_DOMAIN)) == 22
#     await enable_all_entities(
#         hass,
#         freezer,
#         config_entry.entry_id,
#         FroniusInverterUpdateCoordinator.default_interval,
#     )
#     assert len(hass.states.async_all(domain_filter=SENSOR_DOMAIN)) == 58
#     assert_state("sensor.symo_20_dc_current", 0)
#     assert_state("sensor.symo_20_energy_day", 10828)
#     assert_state("sensor.symo_20_total_energy", 44186900)
#     assert_state("sensor.symo_20_energy_year", 25507686)
#     assert_state("sensor.symo_20_dc_voltage", 16)
#     assert_state("sensor.symo_20_status_message", "startup")
