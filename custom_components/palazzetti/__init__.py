"""
The "palazzetti" custom component.
Configuration:
To use the palazzetti component you will need to add the integration from
the integration menu and set the ip of the Connection Box when asked
"""
import logging, asyncio
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import (
    async_track_time_interval,
)
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.const import ATTR_ENTITY_ID
from .const import DOMAIN, INTERVAL, INTERVAL_CNTR, INTERVAL_STDT, INTERVAL_KPAL
from .input_number import create_input_number
from .helper import setup_platform
import voluptuous as vol
from .palazzetti_sdk_local_api import Palazzetti, PalDiscovery

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    "binary_sensor",
    "switch",
    "sensor",
    "input_number",
    # "climate",
    "cover",
]

PLATFORMS_2 = [
    "binary_sensor",
    "switch",
    "sensor",
    # "input_number",
    # "climate",
    "cover",
]

LISTENERS = [
    "_listener_alls",
    "_listener_cntr",
    "_listener_stdt",
    "_listener_kalive",
]


async def async_keep_alive(hass: HomeAssistant, entry: ConfigEntry):
    check_api = PalDiscovery()
    check_ip = await check_api.checkIP(entry.data["host"])

    if check_ip:
        print("IP now reachable")
        await hass.config_entries.async_reload(entry.entry_id)
    else:
        print("IP not reachable")


async def async_upd_alls(hass: HomeAssistant, entry: ConfigEntry):
    if entry.entry_id not in hass.data[DOMAIN]:
        return
    else:
        _api = hass.data[DOMAIN][entry.entry_id]
        await _api.async_get_alls()


async def async_upd_cntr(hass: HomeAssistant, entry: ConfigEntry):
    if entry.entry_id not in hass.data[DOMAIN]:
        return
    _api = hass.data[DOMAIN][entry.entry_id]
    await _api.async_get_cntr()


async def async_upd_stdt(hass: HomeAssistant, entry: ConfigEntry):
    if entry.entry_id not in hass.data[DOMAIN]:
        return
    _api = hass.data[DOMAIN][entry.entry_id]
    await _api.async_get_stdt()


async def async_create_platforms(hass: HomeAssistant, entry: ConfigEntry):
    print("Creating platforms")

    my_api = hass.data[DOMAIN][entry.entry_id]
    await my_api.async_get_alls()
    await my_api.async_get_stdt()
    await my_api.async_get_cntr()
    _config = my_api.get_data_config_json()

    await setup_platform(hass, "input_number")

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


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the GitHub Custom component from yaml configuration."""
    print("Lancia async_setup")
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.debug("Init of palazzetti component")
    print("Lancia async_setup_entry")
    # check and remove keep alive loop data
    kalive_key = entry.entry_id + "_listener_kalive"
    if kalive_key in hass.data[DOMAIN]:
        # remove listener
        hass.data[DOMAIN][kalive_key]()
        # cleanup hass.data
        hass.data[DOMAIN].pop(kalive_key)

    # load last known configuration
    #  _config = entry.data["stove"]
    # checks IP
    check_api = PalDiscovery()
    check_ip = await check_api.checkIP(entry.data["host"])

    if not check_ip:
        print("IP is unreachable")
        # setup platform for binary_sensors only
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, "binary_sensor")
        )
        # keep alive loop until ip is reachable
        def keep_alive(event_time):
            return asyncio.run_coroutine_threadsafe(
                async_keep_alive(hass, entry), hass.loop
            )

        # activate a keep alive loop
        listener_kalive = async_track_time_interval(hass, keep_alive, INTERVAL_KPAL)
        hass.data[DOMAIN][entry.entry_id + "_listener_kalive"] = listener_kalive
        return True

    print("IP is reachable")

    # loop for get dynamic data of stove
    def update_state_datas(event_time):
        return asyncio.run_coroutine_threadsafe(async_upd_alls(hass, entry), hass.loop)

    # loop for get counters data of stove
    def update_cntr_datas(event_time):
        return asyncio.run_coroutine_threadsafe(async_upd_cntr(hass, entry), hass.loop)

    # loop for get static data of stove
    def update_static_datas(event_time):
        return asyncio.run_coroutine_threadsafe(async_upd_stdt(hass, entry), hass.loop)

    # entry.unique_id is generated by the Palazzetti Class during the config_flow
    # and is normally the SN or the MAC address if SN is missing
    api = Palazzetti(entry.data["host"], entry.unique_id)
    # entry.entry_id is generated by HA at the end of the config_flow
    # and is the GUID of the config_entry
    hass.data[DOMAIN][entry.entry_id] = api
    # create platforms at setup only if IP is reachable
    # manages the situation in which HA is rebooted and the device
    # is temporary not available ()
    listener_alls = async_track_time_interval(hass, update_state_datas, INTERVAL)
    hass.data[DOMAIN][entry.entry_id + "_listener_alls"] = listener_alls
    listener_cntr = async_track_time_interval(hass, update_cntr_datas, INTERVAL_CNTR)
    hass.data[DOMAIN][entry.entry_id + "_listener_cntr"] = listener_cntr
    listener_stdt = async_track_time_interval(hass, update_static_datas, INTERVAL_STDT)
    hass.data[DOMAIN][entry.entry_id + "_listener_stdt"] = listener_stdt
    await async_create_platforms(hass, entry)

    # services
    print("Creating service")

    # servizio set setpoint
    myids = []
    # mydata_domain = hass.data[DOMAIN]
    # for product in mydata_domain:
    #     if "listener" in product:
    #         continue
    #     apitest = hass.data[DOMAIN][product]
    #     if apitest.get_data_config_json()["_flag_has_setpoint"]:
    #         myids.append(DOMAIN + "." + apitest.product_id + "_stove")

    SET_SCHEMA = vol.Schema(
        {
            vol.Required(ATTR_ENTITY_ID): vol.In(myids),
            # vol.Optional(ATTR_ENTITY_ID): cv.entity_id,
            vol.Required("value"): cv.string,
        }
    )

    async def set_setpoint(call):
        """Handle the service call 'set'"""

        # mydata = call
        _api = None
        myentity = call.data["entity_id"][11:-6]
        # myentity2 = base
        mydata_domain = hass.data[DOMAIN]
        # mydata_entry = entry
        for product in mydata_domain:
            apitest = hass.data[DOMAIN][product]
            if apitest.product_id == myentity:
                _api = apitest
        if _api:
            myvalue = call.data["value"]
            await _api.async_set_setpoint(myvalue)

    hass.services.async_register(DOMAIN, "set_setpoint", set_setpoint, SET_SCHEMA)

    # servizio set silent
    myids2 = []
    # mydata_domain = hass.data[DOMAIN]
    # for product in mydata_domain:
    #     if "listener" in product:
    #         continue
    #     apitest = hass.data[DOMAIN][product]
    #     if apitest.get_data_config_json()["_flag_has_fan_zero_speed_fan"]:
    #         myids2.append(DOMAIN + "." + apitest.product_id + "_stove")

    SET_SCHEMA = vol.Schema(
        {
            vol.Required(ATTR_ENTITY_ID): vol.In(myids2),
        }
    )

    async def set_silent(call):
        """Handle the service call 'set'"""

        # mydata = call
        _api = None
        myentity = call.data["entity_id"][11:-6]
        # myentity2 = base
        mydata_domain = hass.data[DOMAIN]
        # mydata_entry = entry
        for product in mydata_domain:
            apitest = hass.data[DOMAIN][product]
            if apitest.product_id == myentity:
                _api = apitest
        if _api:
            await _api.async_set_fan_silent_mode()

    hass.services.async_register(DOMAIN, "set_silent", set_silent, SET_SCHEMA)

    # Return boolean to indicate that initialization was successfully.
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS_2
            ]
        )
    )

    # if unload_ok:
    for mylistener in LISTENERS:
        if entry.entry_id + str(mylistener) in hass.data[DOMAIN]:
            hass.data[DOMAIN][entry.entry_id + str(mylistener)]()
            hass.data[DOMAIN].pop(entry.entry_id + str(mylistener))

    if entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(entry.entry_id)

    # return unload_ok
    return True