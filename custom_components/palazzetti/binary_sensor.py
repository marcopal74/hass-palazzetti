from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_CONNECTIVITY,
    BinarySensorEntity,
)

from .const import DOMAIN, COMPANY


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the binary sensors to handle connectivity status of Hub and Product"""
    myhub = hass.data[DOMAIN][config_entry.entry_id]
    list_binary = []

    # Hub connectivity sensor
    list_binary.append(
        PalBinarySensor(
            config_entry.unique_id,
            myhub,
            "hub",
            myhub.hub_name,
            DEVICE_CLASS_CONNECTIVITY,
            deviceid=myhub.hub_id,
        )
    )

    # Product connectivity sensor
    list_binary.append(
        PalBinarySensor(
            config_entry.unique_id,
            myhub,
            "prod",
            "Product",
            DEVICE_CLASS_CONNECTIVITY,
            deviceid=myhub.hub_id + "_prd",  # aka: myhub.product.product_id
        )
    )

    # MyCli-mate 1..3 connectivity sensor
    # only if Product is online

    # Shape connectivity sensor
    # only if Product is online

    async_add_entities(list_binary)


class PalBinarySensor(BinarySensorEntity):
    """representation of a Demo binary sensor."""

    should_poll = False

    def __init__(
        self,
        myid,
        myhub,
        key,
        name,
        device_class,
        deviceid=None,
    ):
        """Initialize the demo sensor."""

        self._id = myid
        self._myhub = myhub
        self._key = key
        self._name = name
        self._sensor_type = device_class
        self._deviceid = deviceid

        # internal variables
        self._product = myhub.product  # it could be offline
        self._ishub = self._key == "hub"

    @property
    def device_info(self):
        if not self._myhub.online:
            return {
                "identifiers": {(DOMAIN, self._deviceid)},
            }

        # Hub is online:
        if self._ishub:
            return {
                "identifiers": {(DOMAIN, self._deviceid)},
                "name": f"{self._name} {self._myhub.get_attributes()['MAC']}",
                "manufacturer": COMPANY,
                "model": self._myhub.get_attributes()["MAC"],
                "sw_version": self._myhub.get_attributes()["SYSTEM"],
            }

        # By now no MyCli-mate or Shape
        return {
            "identifiers": {(DOMAIN, self._deviceid)},
            "name": self._myhub.label,
            "manufacturer": COMPANY,
            "model": self._product.get_key("SN"),
            "sw_version": f"mod {self._product.get_key('MOD')} v{self._product.get_key('VER')} {self._product.get_key('FWDATE')}",
            "via_device": (DOMAIN, self._myhub.hub_id),
        }

    @property
    def unique_id(self):
        """Return the name of the sensor."""
        # either _hub or _prod
        return self._id + "_" + self._key

    @property
    def device_class(self):
        """Return the class of this sensor."""
        return self._sensor_type

    @property
    def name(self):
        """Return the name of the binary sensor."""
        # either ConnBox, BioCC or Product
        return self._name

    @property
    def icon(self):
        """Return the icon of the sensor."""
        if self.is_on:
            if self._ishub:
                return "mdi:server-network"
            return "mdi:link"
        else:
            if self._ishub:
                return "mdi:server-network-off"
            return "mdi:link-off"

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        if not self._myhub.online:
            return False

        if self._ishub:
            return self._myhub.online

        return self._myhub.product_online

        # Option "2": relays on product status and nor APLCONN key
        # if self._product:
        #     return self._product.online

        # return False

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        if not self._myhub.online:
            return None

        if self._ishub:
            cbox_attrib = self._myhub.get_attributes()
            return cbox_attrib

        _prod_attrib = {}
        if not self._myhub.product_online:
            _prod_attrib.update({"icon": "mdi:link-off"})
            return _prod_attrib

        if self._product:
            _prod_attrib = self._product.get_prod_data_json()
            _prod_attrib.update({"icon": "mdi:link"})
            return _prod_attrib

        return None

    async def async_added_to_hass(self):
        """Run when this Entity has been added to HA."""
        # Sensors should also register callbacks to HA when their state changes
        if self._ishub:
            self._myhub.register_callback(self.async_write_ha_state)
        if self._product is not None:
            self._product.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Entity being removed from hass."""
        # The opposite of async_added_to_hass. Remove any registered call backs here.
        if self._ishub:
            self._myhub.remove_callback(self.async_write_ha_state)
        if self._product is not None:
            self._product.remove_callback(self.async_write_ha_state)

    async def async_update(self):
        print(f"binary_sensor PalBinarySensor update: {self._key}")
