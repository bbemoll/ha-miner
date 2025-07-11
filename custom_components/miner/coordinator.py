"""Miner DataUpdateCoordinator."""
import logging
#EBE
_LOGGER = logging.getLogger(__name__)

from datetime import timedelta
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
    _LOGGER.warning(f"EBE_20250711: coordinator.py: could not import pyasic: {PYASIC_VERSION}")
    raise ImportError
#EBE
_LOGGER.warning(f"EBE_20250711: coordinator.py: pyasic successfully loaded")

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed

from .const import CONF_IP
from .const import CONF_MIN_POWER
from .const import CONF_MAX_POWER
from .const import CONF_RPC_PASSWORD
from .const import CONF_SSH_PASSWORD
from .const import CONF_SSH_USERNAME
from .const import CONF_WEB_PASSWORD
from .const import CONF_WEB_USERNAME

#EBE
#_LOGGER = logging.getLogger(__name__)

# Matches iotwatt data log interval
REQUEST_REFRESH_DEFAULT_COOLDOWN = 5

DEFAULT_DATA = {
    "hostname": None,
    "mac": None,
    "make": None,
    "model": None,
    "ip": None,
    "is_mining": False,
    "fw_ver": None,
    "miner_sensors": {
        "hashrate": 0,
        "ideal_hashrate": 0,
#EBE
#        "active_preset_name": None,
        "temperature": 0,
        "power_limit": 0,
        "miner_consumption": 0,
        "efficiency": 0.0,
    },
    "board_sensors": {},
    "fan_sensors": {},
    "config": {},
}


class MinerCoordinator(DataUpdateCoordinator):
    """Class to manage fetching update data from the Miner."""

    miner: pyasic.AnyMiner = None

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize MinerCoordinator object."""
        self.miner = None
        self._failure_count = 0
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            config_entry=entry,
            name=entry.title,
            update_interval=timedelta(seconds=10),
            request_refresh_debouncer=Debouncer(
                hass,
                _LOGGER,
                cooldown=REQUEST_REFRESH_DEFAULT_COOLDOWN,
                immediate=True,
            ),
        )

    @property
    def available(self):
        """Return if device is available or not."""
        return self.miner is not None

    async def get_miner(self):
        """Get a valid Miner instance."""
#EBE
        _LOGGER.warning(f"EBE_20250707: coordinator.py: entering get_miner()")
        miner_ip = self.config_entry.data[CONF_IP]
        miner = await pyasic.get_miner(miner_ip)
        if miner is None:
            return None

#EBE
        _LOGGER.warning(f"EBE_20250707: coordinator.py: miner successfully loaded: miner: {miner}")
        self.miner = miner
        if self.miner.api is not None:
            if self.miner.api.pwd is not None:
                self.miner.api.pwd = self.config_entry.data.get(CONF_RPC_PASSWORD, "")

#EBE
#        _LOGGER.warning(f"LOG_EBE L120: self.miner.api.pwd: {self.miner.api.pwd}")
        if self.miner.web is not None:
            self.miner.web.username = self.config_entry.data.get(CONF_WEB_USERNAME, "")
            self.miner.web.pwd = self.config_entry.data.get(CONF_WEB_PASSWORD, "")

#EBE
#        _LOGGER.warning(f"LOG_EBE L120: self.miner.web.username: {self.miner.web.username}")
#        _LOGGER.warning(f"LOG_EBE L120: self.miner.web.pwd: {self.miner.web.pwd}")
        if self.miner.ssh is not None:
            self.miner.ssh.username = self.config_entry.data.get(CONF_SSH_USERNAME, "")
            self.miner.ssh.pwd = self.config_entry.data.get(CONF_SSH_PASSWORD, "")
#EBE
#        _LOGGER.warning(f"LOG_EBE L120: self.miner.ssh.username: {self.miner.ssh.username}")
#        _LOGGER.warning(f"LOG_EBE L120: self.miner.ssh.pwd: {self.miner.ssh.pwd}")
        return self.miner

    async def _async_update_data(self):
        """Fetch sensors from miners."""

#EBE
        _LOGGER.warning(f"EBE_20250707: coordinator.py: entering _async_update_data()")
        miner = await self.get_miner()

        if miner is None:
            self._failure_count += 1

            if self._failure_count == 1:
                _LOGGER.warning(
                    "Miner is offline – returning zeroed data (first failure)."
                )
                return {
                    **DEFAULT_DATA,
                    "power_limit_range": {
                        "min": self.config_entry.data.get(CONF_MIN_POWER, 100),
                        "max": self.config_entry.data.get(CONF_MAX_POWER, 10000),
                    },
                }

            raise UpdateFailed("Miner Offline (consecutive failure)")

        # At this point, miner is valid
        _LOGGER.debug(f"Found miner: {self.miner}")

#EBE
#        _LOGGER.warning(f"LOG_EBE L152: Found miner: {self.miner}")
#        _LOGGER.warning(f"LOG_EBE L152: miner._rpc_cls: {self.miner._rpc_cls}")
#        _LOGGER.warning(f"LOG_EBE L152: miner._ssh_cls: {self.miner._ssh_cls}")
#        _LOGGER.warning(f"LOG_EBE L152: miner.data_locations: {self.miner.data_locations}")

#EBE
        _LOGGER.warning(f"EBE_20250707: coordinator.py: miner successfully updated: self.miner: {self.miner}")
        try:
            miner_data = await self.miner.get_data(
                include=[
                    pyasic.DataOptions.HOSTNAME,
                    pyasic.DataOptions.MAC,
                    pyasic.DataOptions.IS_MINING,
                    pyasic.DataOptions.FW_VERSION,
                    pyasic.DataOptions.HASHRATE,
#EBE
#                    pyasic.DataOptions.EXPECTED_HASHRATE,
                    pyasic.DataOptions.HASHBOARDS,
                    pyasic.DataOptions.WATTAGE,
                    pyasic.DataOptions.WATTAGE_LIMIT,
                    pyasic.DataOptions.FANS,
                    pyasic.DataOptions.CONFIG,
                ]
            )
        except Exception as err:
            self._failure_count += 1

            if self._failure_count == 1:
                _LOGGER.warning(
                    f"Error fetching miner data: {err} – returning zeroed data (first failure)."
                )
                return {
                    **DEFAULT_DATA,
                    "power_limit_range": {
                        "min": self.config_entry.data.get(CONF_MIN_POWER, 100),
                        "max": self.config_entry.data.get(CONF_MAX_POWER, 10000),
                    },
                }

            _LOGGER.exception(err)
            raise UpdateFailed from err

        _LOGGER.debug(f"Got data: {miner_data}")


#EBE
        _LOGGER.warning(f"EBE_20250707: coordinator.py: found miner_data: {miner_data}")
        _LOGGER.warning(f"EBE_20250707: coordinator.py: miner_data"
              f"\n  IsMining: {miner_data.is_mining}"
              f"\n  Wattage: {miner_data.wattage}"
              f"\n  Hashrate: {miner_data.hashrate}"
              f"\n  WattageLimit: {miner_data.wattage_limit}"
              f"\n  ExpectedHashrate: {miner_data.expected_hashrate}"
              )
#EBE            
#        _LOGGER.warning(f"LOG_EBE L177: miner_data.mac: {miner_data.mac}")
#        _LOGGER.warning(f"LOG_EBE L177: miner_data.api_ver: {miner_data.api_ver}")
#        _LOGGER.warning(f"LOG_EBE L177: miner_data.fw_ver: {miner_data.fw_ver}")
#        _LOGGER.warning(f"LOG_EBE L177: miner_data.hostname: {miner_data.hostname}")
#        _LOGGER.warning(f"LOG_EBE L177: miner_data.hashrate: {miner_data.hashrate}")
#        _LOGGER.warning(f"LOG_EBE L177: miner_data.expected_hashrate: {miner_data.expected_hashrate}")
#        _LOGGER.warning(f"LOG_EBE L177: miner_data.hashboards: {miner_data.hashboards}")
#        _LOGGER.warning(f"LOG_EBE L177: miner_data.env_temp: {miner_data.env_temp}")
#        _LOGGER.warning(f"LOG_EBE L177: miner_data.wattage: {miner_data.wattage}")
#        _LOGGER.warning(f"LOG_EBE L177: miner_data.wattage_limit: {miner_data.wattage_limit}")
#        _LOGGER.warning(f"LOG_EBE L177: miner_data.fans: {miner_data.fans}")
#        _LOGGER.warning(f"LOG_EBE L177: miner_data.fan_psu: {miner_data.fan_psu}")
#        _LOGGER.warning(f"LOG_EBE L177: miner_data.errors: {miner_data.errors}")
#        _LOGGER.warning(f"LOG_EBE L177: miner_data.fault_light: {miner_data.fault_light}")
#        _LOGGER.warning(f"LOG_EBE L177: miner_data.is_mining: {miner_data.is_mining}")
#        _LOGGER.warning(f"LOG_EBE L177: miner_data.uptime: {miner_data.uptime}")
#        _LOGGER.warning(f"LOG_EBE L177: miner_data.config: {miner_data.config}")
#        _LOGGER.warning(f"LOG_EBE L177: miner_data.pools: {miner_data.pools}")

##        miner.expected_hashrate = 
##        _LOGGER.warning(f"LOG_EBE L177: miner_data.expected_hashrate: {miner_data.expected_hashrate}")

##        try:
##            hashrate_calculated = round(float( (257*1000000000000)/5346 * miner_data.wattage_limit ), 2)
##        except TypeError:
##            hashrate_calculated = None

##        _LOGGER.warning(f"LOG_EBE L177: hashrate_calculated: {hashrate_calculated}")
        # Success: reset the failure count
        self._failure_count = 0

        try:
#EBE
#            hashrate = round(float(miner_data.hashrate), 2)
            hashrate = round(float(miner_data.hashrate/1000000000000), 2)
        except TypeError:
            hashrate = None

        try:
#EBE
#            expected_hashrate = round(float(miner_data.expected_hashrate), 2)
#            expected_hashrate = round(float(miner_data.expected_hashrate/1000000000000), 2)
#            expected_hashrate = round(float( (257*1000000000000)/5346 * miner_data.wattage_limit / 1000000000000 ), 2)
            expected_hashrate = 257.0
        except TypeError:
            expected_hashrate = None

#EBE
        try:
            if hashrate <= 0:
                efficiency = round(float(miner_data.wattage/(hashrate+0.01)), 2)
            else:
                efficiency = round(float(miner_data.wattage/hashrate), 2)
        except TypeError:
            efficiency = None
#EBE
        try:
            if miner_data.wattage > 50.0 and miner_data.hashrate > 0.0:
                miner_data.is_mining = True
            else:
                miner_data.is_mining = False
        except TypeError:
            miner_data.is_mining = None

        max_chip_temperature = 0.0
        for i in range(0, len(miner_data.hashboards)):
            if miner_data.hashboards[i].chip_temp > max_chip_temperature:
                max_chip_temperature = round(float(miner_data.hashboards[i].chip_temp), 2)

        data = {
            "hostname": miner_data.hostname,
            "mac": miner_data.mac,
            "make": miner_data.make,
            "model": miner_data.model,
            "ip": self.miner.ip,
            "is_mining": miner_data.is_mining,
            "fw_ver": miner_data.fw_ver,
            "miner_sensors": {
                "hashrate": hashrate,
                "ideal_hashrate": expected_hashrate,
#EBE
#                "active_preset_name": miner_data.config.mining_mode.active_preset.name,
                "temperature": miner_data.temperature_avg,
                "power_limit": miner_data.wattage_limit,
                "miner_consumption": miner_data.wattage,
#EBE
#                "efficiency": miner_data.efficiency,
                "efficiency": efficiency,
            },
            "board_sensors": {
                board.slot: {
                    "board_temperature": board.temp,
                    "chip_temperature": board.chip_temp,
                    "board_hashrate": round(float(board.hashrate or 0), 2),
                }
                for board in miner_data.hashboards
            },
            "fan_sensors": {
                idx: {"fan_speed": fan.speed} for idx, fan in enumerate(miner_data.fans)
            },
            "config": miner_data.config,
            "power_limit_range": {
                "min": self.config_entry.data.get(CONF_MIN_POWER, 100),
                "max": self.config_entry.data.get(CONF_MAX_POWER, 10000),
            },
        }
#EBE
        _LOGGER.warning(f"EBE_20250707: prepared data: {data}")
        _LOGGER.warning(f"EBE_20250707: coordinator.py: prepared data"
              f"\n  IsMining: {miner_data.is_mining}"
              f"\n  Wattage: {miner_data.wattage}"
              f"\n  Hashrate: {miner_data.hashrate}"
              f"\n  WattageLimit: {miner_data.wattage_limit}"
              f"\n  ExpectedHashrate: {miner_data.expected_hashrate}"
              f"\n  MaxChipTemperature: {max_chip_temperature}"
              )
        return data
