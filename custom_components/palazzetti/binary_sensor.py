"""Demo platform that has two fake binary sensors."""
from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_CONNECTIVITY,
    DEVICE_CLASS_MOTION,
    BinarySensorEntity,
)
from .palazzetti_sdk_local_api import PalDiscovery
from . import DOMAIN


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Demo config entry."""
    hubname = "ConnBox"
    if config_entry.data["hub_isbiocc"]:
        hubname = "BioCC"
    # setup while the product is offline
    if config_entry.entry_id not in hass.data[DOMAIN]:
        async_add_entities(
            [
                PalBinarySensor(
                    config_entry.unique_id,
                    None,
                    "hub",
                    hubname,
                    DEVICE_CLASS_CONNECTIVITY,
                    hubid=config_entry.data["hub_id"],
                )
            ]
        )
    else:
        product = hass.data[DOMAIN][config_entry.entry_id].product
        # _config = product.get_data_config_json()
        # _data = product.get_data_json()
        # _states = product.get_data_states()

        list_binary = []

        # Hubb gateway binary_sensor
        list_binary.append(
            PalBinarySensor(
                config_entry.unique_id,
                product,
                "hub",
                hubname,
                DEVICE_CLASS_CONNECTIVITY,
                # hubid=product.hub_id,
                hubid=config_entry.data["hub_id"],
            )
        )

        # Product detection sensor
        list_binary.append(
            PalBinarySensor(
                config_entry.unique_id, product, "prod", "Prodotto", DEVICE_CLASS_MOTION
            )
        )
        async_add_entities(list_binary)


class PalBinarySensor(BinarySensorEntity):
    """representation of a Demo binary sensor."""

    should_poll = False

    def __init__(
        self,
        myid,
        product,
        unique_id,
        name,
        device_class,
        hubid=None,
    ):
        """Initialize the demo sensor."""
        self._product = product
        self._key = unique_id
        self._id = myid
        self._name = name
        if product:
            self._state = product.online
        else:
            self._state = False
        self._sensor_type = device_class
        self._ishub = self._key == "hub"
        self._hubid = hubid

    async def async_added_to_hass(self):
        """Run when this Entity has been added to HA."""
        # Sensors should also register callbacks to HA when their state changes
        if self._product is not None:
            self._product.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Entity being removed from hass."""
        # The opposite of async_added_to_hass. Remove any registered call backs here.
        if self._product is not None:
            self._product.remove_callback(self.async_write_ha_state)

    @property
    def device_info(self):
        if self._product == None:
            return {
                "identifiers": {(DOMAIN, self._hubid)},
            }
        elif self._ishub:
            return {
                "identifiers": {(DOMAIN, self._hubid)},
                "name": f"{self._name} {self._product.get_key('MAC')}",
                "manufacturer": "Palazzetti Lelio S.p.A.",
                "model": self._product.get_key("MAC"),
                "sw_version": self._product.get_key("SYSTEM"),
            }
        return {
            "identifiers": {(DOMAIN, self._product.product_id)},
            "name": self._product.get_key("LABEL"),
            "manufacturer": "Palazzetti Lelio S.p.A.",
            "model": self._product.get_key("SN"),
            "sw_version": f"mod {self._product.get_key('MOD')} v{self._product.get_key('VER')} {self._product.get_key('FWDATE')}",
            "via_device": (DOMAIN, self._product.hub_id),
        }

    @property
    def unique_id(self):
        """Return the name of the sensor."""
        return self._id + "_" + self._key

    @property
    def device_class(self):
        """Return the class of this sensor."""
        return self._sensor_type

    # @property
    # def should_poll(self):
    #     """No polling needed for a demo binary sensor."""
    #     return self._product is not None

    @property
    def name(self):
        """Return the name of the binary sensor."""
        return self._name

    @property
    def icon(self):
        """Return the icon of the sensor."""
        # product is not reachable
        if self._product == None:
            return "mdi:server-network-off"
        if (not self._ishub) and self._product.online:
            return "mdi:link"
        elif (not self._ishub) and (not self._product.online):
            return "mdi:link-off"

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        if self._product == None:
            return False

        return self._product.online

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        if self._product == None:
            return False

        _prod_attrib = self._product.get_prod_data_json()
        _prod_attrib.update({"icon": "mdi:link"})
        if self._ishub:
            cbox_attrib = self._product.get_cb_data_json()
            return cbox_attrib

        return _prod_attrib

    async def async_update(self):
        print(f"binary_sensor PalBinarySensor update {self._key}")

    # async def async_update(self):
    #     """Fetch new state data for the sensor.


#
#     This is the only method that should fetch new data for Home Assistant.
#     """
#     if self._product == None and self._key == "hub":
#         check_api = PalDiscovery()
#         check_ip = await check_api.checkIP(self._myhost)
#
#         if check_ip:
#             print("IP now reachable")
#             # clean up all
#             # myplatform = get_platform(hass, "binary_sensor")
#             # if myplatform.entities and entry.state != "not_loaded":
#             # await hass.config_entries.async_forward_entry_unload(entry, "binary_sensor")
#             # re launch setup
#             await self.hass.config_entries.async_reload(self._entryid)
#         else:
#             print("IP not reachable")
#     else:
#         print("binary update")
