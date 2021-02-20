"""Demo platform that has two fake binary sensors."""
from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_CONNECTIVITY,
    BinarySensorEntity,
)
from . import DOMAIN


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Demo config entry."""
    myhub = hass.data[DOMAIN][config_entry.entry_id]
    list_binary = []
    # setup Hub connectivity sensor
    list_binary.append(
        PalBinarySensor(
            config_entry.unique_id,
            myhub,
            None,
            "hub",
            myhub.hub_name,
            DEVICE_CLASS_CONNECTIVITY,
            hubid=config_entry.data["hub_id"],
        )
    )
    # if myhub.online or (1 == 1):

    product = myhub.product

    # Product detection sensor
    list_binary.append(
        PalBinarySensor(
            config_entry.unique_id,
            myhub,
            product,
            "prod",
            "Prodotto",
            DEVICE_CLASS_CONNECTIVITY,
        )
    )

    async_add_entities(list_binary)


class PalBinarySensor(BinarySensorEntity):
    """representation of a Demo binary sensor."""

    should_poll = False

    def __init__(
        self,
        myid,
        myhub,
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
        self._myhub = myhub
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

    @property
    def device_info(self):
        if not self._myhub.online:
            if self._ishub:
                return {
                    "identifiers": {(DOMAIN, self._hubid)},
                }
            return {
                "identifiers": {(DOMAIN, self._myhub.hub_id + "_prd")},
            }

        # Hub is online:
        if self._ishub:
            return {
                "identifiers": {(DOMAIN, self._hubid)},
                "name": f"{self._name} {self._myhub.get_attributes()['MAC']}",
                "manufacturer": "Palazzetti Lelio S.p.A.",
                "model": self._myhub.get_attributes()["MAC"],
                "sw_version": self._myhub.get_attributes()["SYSTEM"],
            }
        return {
            "identifiers": {(DOMAIN, self._product.product_id)},
            "name": self._product.get_key("LABEL"),
            "manufacturer": "Palazzetti Lelio S.p.A.",
            "model": self._product.get_key("SN"),
            "sw_version": f"mod {self._product.get_key('MOD')} v{self._product.get_key('VER')} {self._product.get_key('FWDATE')}",
            "via_device": (DOMAIN, self._myhub.hub_id),
        }

    @property
    def unique_id(self):
        """Return the name of the sensor."""
        return self._id + "_" + self._key

    @property
    def device_class(self):
        """Return the class of this sensor."""
        return self._sensor_type

    @property
    def name(self):
        """Return the name of the binary sensor."""
        return self._name

    @property
    def icon(self):
        """Return the icon of the sensor."""
        # product is not reachable
        if not self._myhub.online:
            if self._ishub:
                return "mdi:server-network-off"
            return "mdi:link-off"

        if self._myhub.online:
            if self._ishub:
                return "mdi:server-network"
            return "mdi:link"

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        if not self._myhub.online:
            return False

        if self._ishub:
            return self._myhub.online

        if self._product:
            return self._product.online

        return False

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        if not self._myhub.online:
            return None

        if self._ishub:
            cbox_attrib = self._myhub.get_attributes()
            return cbox_attrib

        _prod_attrib = self._product.get_prod_data_json()
        _prod_attrib.update({"icon": "mdi:link"})
        return _prod_attrib

    async def async_update(self):
        print(f"binary_sensor PalBinarySensor update {self._key}")
