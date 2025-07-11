"""Support for Bitcoin ASIC miners."""
from __future__ import annotations

import logging
#EBE
_LOGGER = logging.getLogger(__name__)

from importlib.metadata import version

from .const import PYASIC_VERSION

try:
    import pyasic
#EBE
#    if not version("pyasic") == PYASIC_VERSION:
#        raise ImportError
except ImportError:
    from .patch import install_package

#EBE
#    install_package(f"pyasic=={PYASIC_VERSION}")
#    import pyasic

#EBE
    _LOGGER.warning(f"EBE_20250711: number.py: could not import pyasic: {PYASIC_VERSION}")
    raise ImportError
#EBE
_LOGGER.warning(f"EBE_20250711: number.py: pyasic successfully loaded")

from homeassistant.components.number import NumberEntityDescription, NumberDeviceClass
from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry
from homeassistant.helpers import entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import EntityCategory
from homeassistant.const import UnitOfPower

from .const import DOMAIN
from .coordinator import MinerCoordinator

#EBE
#_LOGGER = logging.getLogger(__name__)


NUMBER_DESCRIPTION_KEY_MAP: dict[str, NumberEntityDescription] = {
    "power_limit": NumberEntityDescription(
        key="Power Limit",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=NumberDeviceClass.POWER,
        entity_category=EntityCategory.CONFIG,
    )
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add sensors for passed config_entry in HA."""
    coordinator: MinerCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    await coordinator.async_config_entry_first_refresh()
#EBE
#    _LOGGER.warning(f"LOG_EBE numbers.py_L60: coordinator.miner: {coordinator.miner}")
#    _LOGGER.warning(f"LOG_EBE numbers.py_L60: coordinator.miner._rpc_cls: {coordinator.miner._rpc_cls}")
#    _LOGGER.warning(f"LOG_EBE numbers.py_L60: coordinator.miner.raw_model: {coordinator.miner.raw_model}")
#    _LOGGER.warning(f"LOG_EBE numbers.py_L60: coordinator.miner.expected_hashboards: {coordinator.miner.expected_hashboards}")
#    _LOGGER.warning(f"LOG_EBE numbers.py_L60: coordinator.miner.expected_chips: {coordinator.miner.expected_chips}")
#    _LOGGER.warning(f"LOG_EBE numbers.py_L60: coordinator.miner.expected_chips: {coordinator.miner.expected_chips}")
#    _LOGGER.warning(f"LOG_EBE numbers.py_L60: coordinator.miner.supports_autotuning: {coordinator.miner.supports_autotuning}")
    if coordinator.miner.supports_autotuning:
        async_add_entities(
            [
                MinerPowerLimitNumber(
                    coordinator=coordinator,
                    entity_description=NUMBER_DESCRIPTION_KEY_MAP["power_limit"],
                )
            ]
        )


class MinerPowerLimitNumber(CoordinatorEntity[MinerCoordinator], NumberEntity):
    """Defines a Miner Number to set the Power Limit of the Miner."""

    def __init__(
        self, coordinator: MinerCoordinator, entity_description: NumberEntityDescription
    ):
        """Initialize the PowerLimit entity."""
        super().__init__(coordinator=coordinator)
        self._attr_native_value = self.coordinator.data["miner_sensors"]["power_limit"]
        self.entity_description = entity_description

    @property
    def name(self) -> str | None:
        """Return name of the entity."""
        return f"{self.coordinator.config_entry.title} Power Limit"

    @property
    def device_info(self) -> entity.DeviceInfo:
        """Return device info."""
        return entity.DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.data["mac"])},
            connections={
                ("ip", self.coordinator.data["ip"]),
                (device_registry.CONNECTION_NETWORK_MAC, self.coordinator.data["mac"]),
            },
            configuration_url=f"http://{self.coordinator.data['ip']}",
            manufacturer=self.coordinator.data["make"],
            model=self.coordinator.data["model"],
            sw_version=self.coordinator.data["fw_ver"],
            name=f"{self.coordinator.config_entry.title}",
        )

    @property
    def unique_id(self) -> str | None:
        """Return device UUID."""
        return f"{self.coordinator.data['mac']}-power_limit"

    @property
    def native_min_value(self) -> float | None:
        """Return device minimum value."""
#EBE
#        return self.coordinator.data["power_limit_range"]["min"]
        return 1800

    @property
    def native_max_value(self) -> float | None:
        """Return device maximum value."""
#EBE
#        return self.coordinator.data["power_limit_range"]["max"]
        return 4500

    @property
    def native_step(self) -> float | None:
        """Return device increment step."""
#EBE
#        return 100
        return 300

    @property
    def native_unit_of_measurement(self):
        """Return device unit of measurement."""
        return "W"

    async def async_set_native_value(self, value):
        """Update the current value."""

        miner = self.coordinator.miner

        _LOGGER.debug(
            f"{self.coordinator.config_entry.title}: setting power limit to {value}."
        )

#EBE
        _LOGGER.warning(f"LOG_EBE numbers.py_L150: coordinator.miner: {self.coordinator.config_entry.title}: setting power limit to {value}.")
#        _LOGGER.warning(f"LOG_EBE numbers.py_L150: miner.supports_autotuning: {miner.supports_autotuning}")
        if not miner.supports_autotuning:
            raise TypeError(
                f"{self.coordinator.config_entry.title}: Tuning not supported."
            )

        result = await miner.set_power_limit(int(value))

#EBE
        _LOGGER.warning(f"LOG_EBE numbers.py_L150: result: {result}")
        if not result:
            raise pyasic.APIError("Failed to set wattage.")

        self._attr_native_value = value
        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        if self.coordinator.data["miner_sensors"]["power_limit"] is not None:
            self._attr_native_value = self.coordinator.data["miner_sensors"][
                "power_limit"
            ]

        super()._handle_coordinator_update()

    @property
    def available(self) -> bool:
        """Return if entity is available or not."""
        return self.coordinator.available
