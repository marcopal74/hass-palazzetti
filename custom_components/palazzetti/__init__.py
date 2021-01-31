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
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.const import ATTR_ENTITY_ID
from .const import DOMAIN, DATA_PALAZZETTI, INTERVAL, INTERVAL_CNTR, INTERVAL_STDT
from .input_number import create_input_number
from .helper import setup_platform, get_platform
import voluptuous as vol
from .palazzetti_sdk_local_api import Palazzetti

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


async def async_upd_alls(hass: HomeAssistant, entry: ConfigEntry):
    _api = hass.data[DOMAIN][entry.entry_id]
    await _api.async_get_alls()
    # await update_states(hass, entry)


async def async_upd_cntr(hass: HomeAssistant, entry: ConfigEntry):
    _api = hass.data[DOMAIN][entry.entry_id]
    await _api.async_get_cntr()
    # await update_states(hass, entry)


async def async_upd_stdt(hass: HomeAssistant, entry: ConfigEntry):
    _api = hass.data[DOMAIN][entry.entry_id]
    await _api.async_get_stdt()
    # await update_states(hass, entry)


# creates states and updates data according to configuration of stove
async def update_states(hass: HomeAssistant, entry: ConfigEntry):
    pass
    # _class_id = entry.unique_id
    # _api = hass.data[DOMAIN][entry.entry_id]


#
# _config = _api.get_data_config_json()
# _config.update({"icon": "mdi:ip-network", "friendly_name": "Configuration"})
#
# _data = _api.get_data_states()
#
# _state_attrib = _api.get_data_json()
# _state_attrib.update({"friendly_name": "Stove"})

# status_icon = "mdi:fireplace-off"
# if _state_attrib["STATUS"] == 6:
#     status_icon = "mdi:fireplace"
# elif _config["_flag_error_status"]:
#     status_icon = "mdi:alert"

# intid=0
# myname=DOMAIN + ".stove"
# while not hass.states.async_available(myname):
#    intid=intid+1
#    myname=f"{DOMAIN}_{intid}.stove"

# hass.states.async_set(
#     DOMAIN + "." + _class_id + "_LABEL",
#     _state_attrib["LABEL"],
#     {"icon": "mdi:tag", "friendly_name": "Label"},
# )

# hass.states.async_set(
#     DOMAIN + "." + _class_id + "_stove", _data["state"], _state_attrib
# )
#
# hass.states.async_set(DOMAIN + "." + _class_id + "_config", _data["ip"], _config)
#
# hass.states.async_set(
#     DOMAIN + "." + _class_id + "_STATUS",
#     _data["status"],
#     {"icon": status_icon, "friendly_name": "Status"},
# )

# device_registry = await dr.async_get_registry(hass)
# device_registry.async_get_or_create(
#     config_entry_id=DOMAIN + "." + _class_id + "_LABEL",
#     # connections={(dr.CONNECTION_NETWORK_MAC, config.mac)},
#     identifiers={(DOMAIN, entry.unique_id)},
#     manufacturer="Palazzetti Lelio S.p.A.",
#     name=_api.get_key("LABEL"),
#     model=_api.get_key("SN"),
#     sw_version=_api.get_key("SYSTEM"),
# )


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
    # await update_states(hass, entry)
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

    # create platforms
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

    # servizio set setpoint
    myids = []
    mydata_domain = hass.data[DOMAIN]
    for product in mydata_domain:
        apitest = hass.data[DOMAIN][product]
        if apitest.get_data_config_json()["_flag_has_setpoint"]:
            myids.append(DOMAIN + "." + apitest.product_id + "_stove")

    SET_SCHEMA = vol.Schema(
        {
            vol.Required(ATTR_ENTITY_ID): vol.In(myids),
            # vol.Optional(ATTR_ENTITY_ID): cv.entity_id,
            vol.Required("value"): cv.string,
        }
    )

    # SET_SCHEMA1 = vol.Schema(
    #     {
    #         vol.Required("value"): cv.string,
    #         vol.Optional(ATTR_ENTITY_ID): vol.In(myids),
    #     }
    # )

    # SET_SCHEMA2 = {
    #     vol.Required("entity_id"): cv.string,
    #     vol.Required("value"): cv.string,
    # }

    # def preprocess_data(data):
    #     """Preprocess the service data."""
    #     base = {
    #         entity_field: data.pop(entity_field)
    #         for entity_field in cv.ENTITY_SERVICE_FIELDS
    #         if entity_field in data
    #     }
    #
    #     base["params"] = data
    #     return base

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

    # async def set_setpoint_e(product, call):
    #     """Handle the service call 'set'"""
    #     mydata = call
    #     _api = None
    #     myentity = call.data["entity-id"][11:-6]
    #     mydata_domain = hass.data[DOMAIN]
    #     mydata_entry = entry
    #     for product in mydata_domain:
    #         apitest = hass.data[DOMAIN][product]
    #         if apitest.product_id == myentity:
    #             _api = apitest
    #     if _api:
    #         myvalue = call.data["value"]
    #         await _api.async_set_setpoint(myvalue)

    # apro la piattaforma degli slider: input_number
    # platform_name = "palazzetti"
    # component = EntityComponent(_LOGGER, DOMAIN, hass)
    # component.async_register_entity_service(
    #     "set_params",
    #     vol.All(cv.make_entity_service_schema(SET_SCHEMA2), preprocess_data),
    #     set_setpoint_e,
    # )
    # component.async_register_entity_service(
    #     "set_setpoint",
    #     SET_SCHEMA1,
    #     "async_set_setpoint",
    # )

    hass.services.async_register(DOMAIN, "set_setpoint", set_setpoint, SET_SCHEMA)

    # servizio set silent
    myids2 = []
    mydata_domain = hass.data[DOMAIN]
    for product in mydata_domain:
        apitest = hass.data[DOMAIN][product]
        if apitest.get_data_config_json()["_flag_has_fan_zero_speed_fan"]:
            myids2.append(DOMAIN + "." + apitest.product_id + "_stove")

    SET_SCHEMA = vol.Schema(
        {
            vol.Required(ATTR_ENTITY_ID): vol.In(myids2),
            # vol.Optional(ATTR_ENTITY_ID): cv.entity_id,
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
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok