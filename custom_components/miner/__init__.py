"""The Miner integration."""
from __future__ import annotations

#EBE
import logging
_LOGGER = logging.getLogger(__name__)

try:
    import pyasic
except ImportError:
    from .patch import install_package
    from .const import PYASIC_VERSION

#EBE
#    install_package(f"pyasic=={PYASIC_VERSION}")
#    import pyasic
#EBE
    _LOGGER.warning(f"EBE_20250711: __init__.py: could not import pyasic: {PYASIC_VERSION}")
    raise ImportError
#EBE
_LOGGER.warning(f"EBE_20250711: __init__.py: pyasic successfully loaded")

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import CONF_IP
from .const import DOMAIN
from .coordinator import MinerCoordinator
from .services import async_setup_services

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.SELECT,
]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Miner from a config entry."""

    miner_ip = config_entry.data[CONF_IP]
    miner = await pyasic.get_miner(miner_ip)

    if miner is None:
        raise ConfigEntryNotReady("Miner could not be found.")

    m_coordinator = MinerCoordinator(hass, config_entry)
    hass.data.setdefault(DOMAIN, {})[config_entry.entry_id] = m_coordinator

    await m_coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    await async_setup_services(hass)


#EBE
    _LOGGER.warning(f"LOG_EBE L55: m_coordinator.miner: {m_coordinator.miner}")
#    _LOGGER.warning(f"LOG_EBE L55: m_coordinator.miner._rpc_cls: {m_coordinator.miner._rpc_cls}")
#    _LOGGER.warning(f"LOG_EBE L55: m_coordinator.miner.raw_model: {m_coordinator.miner.raw_model}")
#    _LOGGER.warning(f"LOG_EBE L55: m_coordinator.miner.expected_hashboards: {m_coordinator.miner.expected_hashboards}")
#    _LOGGER.warning(f"LOG_EBE L55: m_coordinator.miner.expected_chips: {m_coordinator.miner.expected_chips}")

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    )
    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok
