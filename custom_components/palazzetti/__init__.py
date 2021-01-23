"""
The "palazzetti" custom component.
Configuration:
To use the palazzetti component you will need to add the integration from
the integration menu and set the ip of the Connection Box when asked
"""
import logging, asyncio
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_time_interval
from .const import DOMAIN, DATA_PALAZZETTI, INTERVAL, INTERVAL_CNTR, INTERVAL_STDT
from .input_number import create_input_number
from .helper import setup_platform
from .palazzetti_sdk_local_api import Palazzetti

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    "switch",
    "sensor",
    "input_number",
    # "fan",
    # "climate",
    "cover",
    "light",
]


async def async_upd_alls(hass: HomeAssistant, entry: ConfigEntry):
    _api = hass.data[DOMAIN][entry.entry_id]
    await _api.async_get_alls()
    await update_states(hass, entry)


async def async_upd_cntr(hass: HomeAssistant, entry: ConfigEntry):
    _api = hass.data[DOMAIN][entry.entry_id]
    await _api.async_get_cntr()
    await update_states(hass, entry)


async def async_upd_stdt(hass: HomeAssistant, entry: ConfigEntry):
    _api = hass.data[DOMAIN][entry.entry_id]
    await _api.async_get_stdt()
    await update_states(hass, entry)


# creates states and updates data according to configuration of stove
async def update_states(hass: HomeAssistant, entry: ConfigEntry):
    _class_id = entry.unique_id
    _api = hass.data[DOMAIN][entry.entry_id]

    _config = _api.get_data_config_json()
    _config.update({"icon": "mdi:ip-network", "friendly_name": "Configuration"})

    _data = _api.get_data_states()

    _state_attrib = _api.get_data_json()
    status_icon = "mdi:fireplace-off"
    if _state_attrib["STATUS"] == 6:
        status_icon = "mdi:fireplace"
    elif _config["_flag_error_status"]:
        status_icon = "mdi:alert"

    # intid=0
    # myname=DOMAIN + ".stove"
    # while not hass.states.async_available(myname):
    #    intid=intid+1
    #    myname=f"{DOMAIN}_{intid}.stove"

    hass.states.async_set(
        _class_id + ".LABEL",
        _state_attrib["LABEL"],
        {"icon": "mdi:tag"},
    )

    hass.states.async_set(_class_id + ".stove", _data["state"], _state_attrib)

    hass.states.async_set(_class_id + ".config", _data["ip"], _config)

    hass.states.async_set(
        _class_id + ".STATUS",
        _data["status"],
        {
            "icon": status_icon,
        },
    )

    # if _config["_flag_has_fan"]:
    #     hass.states.async_set(
    #         _class_id + ".F2L",
    #         _state_attrib["F2L"],
    #         {"icon": "mdi:fan"},
    #     )

    # hass.states.async_set(
    #     _class_id + ".PWR",
    #     _state_attrib["PWR"],
    #     {"icon": "mdi:fire"},
    # )

    # if _config["_flag_has_setpoint"]:
    #     hass.states.async_set(
    #         _class_id + ".SETP",
    #         _state_attrib["SETP"],
    #         {
    #             "friendly_name": "Setpoint",
    #             "unit_of_measurement": "°C",
    #             "icon": "hass:thermometer",
    #         },
    #     )


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the GitHub Custom component from yaml configuration."""
    print("Lancia async_setup")
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.debug("Init of palazzetti component")
    print("Lancia async_setup_entry")

    await setup_platform(hass, "input_number")

    # to be used to define unique id for instance
    class_id = entry.unique_id

    api = Palazzetti(entry.data["host"], class_id)
    hass.data[DATA_PALAZZETTI + class_id] = api
    hass.data[DOMAIN][entry.entry_id] = api

    await api.async_get_alls()
    await api.async_get_stdt()
    await api.async_get_cntr()
    await update_states(hass, entry)
    _config = api.get_data_config_json()

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
    print("Creating platforms")
    for component in PLATFORMS:
        if component == "cover":
            if _config["_flag_has_door_control"]:
                hass.async_create_task(
                    hass.config_entries.async_forward_entry_setup(entry, component)
                )
        elif component == "climate":
            if _config["_flag_has_setpoint"]:
                hass.async_create_task(
                    hass.config_entries.async_forward_entry_setup(entry, component)
                )
        elif component == "light":
            if _config["_flag_has_light_control"]:
                hass.async_create_task(
                    hass.config_entries.async_forward_entry_setup(entry, component)
                )
        elif component == "fan":
            if _config["_flag_has_fan"]:
                hass.async_create_task(
                    hass.config_entries.async_forward_entry_setup(entry, component)
                )
        elif component == "input_number":
            hass.async_create_task(create_input_number(hass, entry))
        else:
            hass.async_create_task(
                hass.config_entries.async_forward_entry_setup(entry, component)
            )

    # services
    print("Creating service")

    def set_parameters(call):
        """Handle the service call 'set'"""
        api.set_parameters(call.data)

    hass.services.async_register(DOMAIN, "set_parms", set_parameters)

    # Return boolean to indicate that initialization was successfully.
    return True


async def finish_setup(hass: HomeAssistant, config: dict):
    """Finish set up once platforms are set up."""
    switches = None

    while not switches:
        # Not all platforms might be loaded.
        if switches is not None:
            await asyncio.sleep(0)
        switches = sorted(hass.states.async_entity_ids("switch"))


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok