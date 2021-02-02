"""Demo platform that has two fake binary sensors."""
from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_CONNECTIVITY,
    DEVICE_CLASS_MOTION,
    BinarySensorEntity,
)

from . import DOMAIN


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Demo config entry."""
    # il prodotto non è stato inserito all'esecuzione dell'async_setup_entry
    if config_entry.entry_id not in hass.data[DOMAIN]:
        async_add_entities(
            [
                PalBinarySensor(
                    config_entry.unique_id,
                    None,
                    "hub",
                    "Hub",
                    DEVICE_CLASS_CONNECTIVITY,
                ),
                PalBinarySensor(
                    config_entry.unique_id,
                    None,
                    "prod",
                    "Prodotto",
                    DEVICE_CLASS_MOTION,
                ),
            ]
        )
    else:
        product = hass.data[DOMAIN][config_entry.entry_id]
        # _config = product.get_data_config_json()
        # _data = product.get_data_json()
        # _states = product.get_data_states()

        list_binary = []

        # according to CBTYPE the hub is the ConnBox or the BioCC
        # if not (_config["_value_product_type"] == 7 or _config["_value_product_type"] == 8):
        if product.hub_isbiocc:
            # c'è la BioCC
            list_binary.append(
                PalBinarySensor(
                    config_entry.unique_id,
                    product,
                    "hub",
                    "BioCC",
                    DEVICE_CLASS_CONNECTIVITY,
                    product.hub_id,
                )
            )
        else:
            # c'è la ConnBox
            list_binary.append(
                PalBinarySensor(
                    config_entry.unique_id,
                    product,
                    "hub",
                    "ConnBox",
                    DEVICE_CLASS_CONNECTIVITY,
                    product.hub_id,
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

    def __init__(self, myid, product, unique_id, name, device_class, mydevice=None):
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
        self._ishub = not (mydevice == None)
        self._mydevice = mydevice

    @property
    def device_info(self):
        if self._product == None:
            return {
                "identifiers": {(DOMAIN, self._id)},
            }
        elif self._ishub:
            return {
                "identifiers": {(DOMAIN, self._mydevice)},
                "name": f"{self._name} {self._product.get_key('MAC')}",
                "manufacturer": "Palazzetti Lelio S.p.A.",
                "model": self._product.get_key("MAC"),
                "sw_version": self._product.get_key("SYSTEM"),
            }
        return {
            "identifiers": {(DOMAIN, self._id)},
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

    @property
    def should_poll(self):
        """No polling needed for a demo binary sensor."""
        return True

    @property
    def name(self):
        """Return the name of the binary sensor."""
        return self._name

    @property
    def icon(self):
        """Return the icon of the sensor."""
        # product is not reachable
        if self._product == None:
            if self._key == "prod":
                return "mdi:link-off"
            else:
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
