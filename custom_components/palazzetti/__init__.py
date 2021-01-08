"""
The "palazzetti" custom component.
Configuration:
To use the palazzetti component you will need to add the integration from
the integration menu and set the ip of the Connection Box when asked
"""
import logging, asyncio, json, requests, voluptuous, aiohttp

from homeassistant import config_entries, core

from .const import DOMAIN, DATA_PALAZZETTI, INTERVAL, INTERVAL_CNTR, INTERVAL_STDT

from .palazzetti_local_api import Palazzetti

from homeassistant.helpers.event import async_track_time_interval
import homeassistant.helpers.config_validation as cv
import time

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = voluptuous.Schema(
    {
        DOMAIN: voluptuous.Schema(
            {
                voluptuous.Required("ip"): cv.string,
            }
        )
    },
    extra=voluptuous.ALLOW_EXTRA,
)


async def async_upd_alls(hass: core.HomeAssistant, _entry: config_entries.ConfigEntry):
    _api = hass.data[DATA_PALAZZETTI + _entry.unique_id]
    await _api.async_get_alls()
    await update_states(hass, _entry)


async def async_upd_cntr(hass: core.HomeAssistant, _entry: config_entries.ConfigEntry):
    _api = hass.data[DATA_PALAZZETTI + _entry.unique_id]
    await _api.async_get_cntr()
    await update_states(hass, _entry)


async def async_upd_stdt(hass: core.HomeAssistant, _entry: config_entries.ConfigEntry):
    _api = hass.data[DATA_PALAZZETTI + _entry.unique_id]
    await _api.async_get_stdt()
    await update_states(hass, _entry)


# creates states and updates data according to configuration of stove
async def update_states(hass: core.HomeAssistant, _entry: config_entries.ConfigEntry):
    _class_id = _entry.unique_id
    _api = hass.data[DATA_PALAZZETTI + _class_id]
    # update parsed configuration
    await _api.async_config_parse()
    _config = _api.get_data_config_json()
    # prendo la parsed configuration dall'entry che ho creato in fase di registrazione dell'oggetto
    # _config = _entry.data["stove"]
    _data = _api.get_data_states()
    _state_attrib = _api.get_data_json()

    _config.update({"icon": "mdi:ip-network", "friendly_name": "Configuration"})
    status_icon = "mdi:fireplace-off"
    if _state_attrib["STATUS"] == 6:
        status_icon = "mdi:fireplace"
    hass.states.async_set(_class_id + ".stove", _data["state"], _state_attrib)
    hass.states.async_set(_class_id + ".config", _data["ip"], _config)
    hass.states.async_set(
        _class_id + ".STATUS",
        _data["status"],
        {"icon": status_icon, "unique_id": _class_id + ".status"},
    )

    if _config["_flag_is_air"]:
        hass.states.async_set(
            _class_id + ".F2L",
            _state_attrib["F2L"],
            {"icon": "mdi:fan", "unique_id": _class_id + ".f2l"},
        )

    hass.states.async_set(
        _class_id + ".PWR",
        _state_attrib["PWR"],
        {"icon": "mdi:fire", "unique_id": _class_id + ".pwr"},
    )
    hass.states.async_set(
        _class_id + ".SETP",
        _state_attrib["SETP"],
        {
            "friendly_name": "Setpoint",
            "unit_of_measurement": "°C",
            "icon": "hass:thermometer",
            "unique_id": _class_id + ".setp",
        },
    )


async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
):
    _LOGGER.debug("Init of palazzetti component")

    # to be used to define unique id for instance
    # class_id = "plz_" + entry.data["host"].replace(".", "")
    class_id = entry.unique_id

    # api = Palazzetti(hass, entry,class_id)
    api = Palazzetti(entry.data["host"], class_id)
    hass.data[DATA_PALAZZETTI + class_id] = api
    await api.async_get_alls()
    # await async_upd_alls(hass,class_id)
    await api.async_get_stdt()
    await api.async_get_cntr()
    await update_states(hass, entry)

    # loop for get dynamic data of stove
    def update_state_datas(event_time):
        # return asyncio.run_coroutine_threadsafe( api.async_get_alls(), hass.loop)
        return asyncio.run_coroutine_threadsafe(async_upd_alls(hass, entry), hass.loop)

    # loop for get counter of stove
    def update_cntr_datas(event_time):
        return asyncio.run_coroutine_threadsafe(async_upd_cntr(hass, entry), hass.loop)

    # loop for get static data of stove
    def update_static_datas(event_time):
        return asyncio.run_coroutine_threadsafe(async_upd_stdt(hass, entry), hass.loop)

    async_track_time_interval(hass, update_state_datas, INTERVAL)
    async_track_time_interval(hass, update_cntr_datas, INTERVAL_CNTR)
    async_track_time_interval(hass, update_static_datas, INTERVAL_STDT)

    # sensor platform
    hass.async_add_job(hass.config_entries.async_forward_entry_setup(entry, "sensor"))

    # services
    def set_parameters(call):
        """Handle the service call 'set'"""
        api.set_parameters(call.data)

    hass.services.async_register(DOMAIN, "set_parms", set_parameters)

    # Return boolean to indicate that initialization was successfully.
    return True


async def async_setup(hass, config):
    """Set up the GitHub Custom component from yaml configuration."""
    return True