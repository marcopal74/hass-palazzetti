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
    _remove_empty_listener,
    async_track_time_interval,
)
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.const import ATTR_ENTITY_ID
from .const import DOMAIN, INTERVAL, INTERVAL_CNTR, INTERVAL_STDT
from .input_number import create_input_number
from .helper import setup_platform, get_platform
import voluptuous as vol
from .palazzetti_sdk_local_api import Palazzetti, PalDiscovery

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    "binary_sensor",
    "switch",
    "sensor",
    "input_number",
    # "fan",
    # "climate",
    "cover",
    # "light",
]

PLATFORMS_2 = [
    "binary_sensor",
    "switch",
    "sensor",
    # "input_number",
    # "fan",
    # "climate",
    "cover",
    # "light",
]

LISTENERS = ["_listener_alls", "_listener_cntr", "_listener_stdt"]


async def async_upd_alls(hass: HomeAssistant, entry: ConfigEntry):
    # if class instance is misssing creates it
    if entry.entry_id not in hass.data[DOMAIN]:
        await async_create_platforms(hass, entry)
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
    _config = None
    if entry.entry_id in hass.data[DOMAIN]:
        # è il primo giro entra qui solo se chimato da async_setup_entry con IP raggiungibile
        pass
    else:
        # tentativo di creazione partendo dall'aggiornamento periodico della GET ALLS
        # quando parte da uno stato non connesso
        check_api = PalDiscovery()
        check_ip = await check_api.checkIP(entry.data["host"])

        if not check_ip:
            print("IP not reachable")
            return

        # the IP is reachable and is a compatible Hub
        class_id = entry.unique_id
        api = Palazzetti(entry.data["host"], class_id)
        # to be removed
        hass.data[DOMAIN][entry.entry_id] = api

    my_api = hass.data[DOMAIN][entry.entry_id]
    await my_api.async_get_alls()
    await my_api.async_get_stdt()
    await my_api.async_get_cntr()
    _config = my_api.get_data_config_json()

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
        elif component == "binary_sensor":
            myplatform = get_platform(hass, component)
            if myplatform:
                await hass.config_entries.async_forward_entry_unload(entry, component)
                hass.async_create_task(
                    hass.config_entries.async_forward_entry_setup(entry, component)
                )
            else:
                hass.async_create_task(
                    hass.config_entries.async_forward_entry_setup(entry, component)
                )
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

    await setup_platform(hass, "input_number")

    # load last known configuration
    #  _config = entry.data["stove"]
    # checks IP
    check_api = PalDiscovery()
    check_ip = await check_api.checkIP(entry.data["host"])

    if check_ip:
        print("IP is reachable")
        # entry.unique_id is generated by the Palazzetti Class during the config_flow
        # and is normally the SN or the MAC address if SN is missing
        api = Palazzetti(entry.data["host"], entry.unique_id)
        # entry.entry_id is generated by HA at the end of the config_flow
        # and is the GUID of the config_entry
        hass.data[DOMAIN][entry.entry_id] = api

    # loop for get dynamic data of stove
    def update_state_datas(event_time):
        return asyncio.run_coroutine_threadsafe(async_upd_alls(hass, entry), hass.loop)

    # loop for get counters data of stove
    def update_cntr_datas(event_time):
        return asyncio.run_coroutine_threadsafe(async_upd_cntr(hass, entry), hass.loop)

    # loop for get static data of stove
    def update_static_datas(event_time):
        return asyncio.run_coroutine_threadsafe(async_upd_stdt(hass, entry), hass.loop)

    listener_alls = async_track_time_interval(hass, update_state_datas, INTERVAL)
    hass.data[DOMAIN][entry.entry_id + "_listener_alls"] = listener_alls
    listener_cntr = async_track_time_interval(hass, update_cntr_datas, INTERVAL_CNTR)
    hass.data[DOMAIN][entry.entry_id + "_listener_cntr"] = listener_cntr
    listener_stdt = async_track_time_interval(hass, update_static_datas, INTERVAL_STDT)
    hass.data[DOMAIN][entry.entry_id + "_listener_stdt"] = listener_stdt

    # create platforms at setup only if IP is reachable
    # manages the situation in which HA is rebooted and the device
    # is temporary not available ()
    if check_ip:
        await async_create_platforms(hass, entry)
    else:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, "binary_sensor")
        )

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

    if unload_ok:
        for mylistener in LISTENERS:
            if entry.entry_id + str(mylistener) in hass.data[DOMAIN]:
                hass.data[DOMAIN][entry.entry_id + str(mylistener)]()
                hass.data[DOMAIN].pop(entry.entry_id + str(mylistener))

        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok