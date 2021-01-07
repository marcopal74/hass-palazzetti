"""Platform for sensor integration."""
import json
from homeassistant.const import (
    TEMP_CELSIUS,
    ATTR_UNIT_OF_MEASUREMENT,
    ATTR_FRIENDLY_NAME,
)
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, DATA_PALAZZETTI


async def async_setup_entry(hass, config_entry, add_entities):
    """Set up the sensor platform from config flow"""
    # ipname=config_entry.data["host"].replace(".","")
    setup_platform(hass, config_entry, add_entities)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform from configuration.yaml"""

    # the sensor unique_id has to be built with the same logic of class_id in the integration __init__
    sensor_id = config.unique_id
    # get the config from the entry: if something changes the integration has to be removed and reinstalled
    _config = config.data["stove"]

    # logica di configurazione delle sonde in base al parse della configurazione
    code_status = {
        "kTemperaturaAmbiente": "Temp. Ambiente",
        "kTemperaturaAccumulo": "Temp. Accumulo",
        "kTemperaturaAcquaMandata": "Temp. Mandata",
    }
    entity_list = []
    # entity_list.append(SensorT1(sensor_id))

    nome_temp = code_status.get(
        _config["value_descrizione_temperatura_aria"],
        _config["value_descrizione_temperatura_aria"],
    )
    if _config["flag_tipologia_idro"]:
        nome_temp = code_status.get(
            _config["value_descrizione_temperatura_idro"],
            _config["value_descrizione_temperatura_idro"],
        )

    # Sonda principale
    entity_list.append(
        SensorX(
            sensor_id,
            _config["value_descrizione_sonda_principale"],
            TEMP_CELSIUS,
            None,
            nome_temp,
        )
    )

    # Setpoint
    entity_list.append(
        SensorX(
            sensor_id,
            "SETP",
            TEMP_CELSIUS,
            None,
            "Setpoint",
        )
    )

    if _config["flag_tipologia_idro"]:
        # T2 Idro
        entity_list.append(
            SensorX(
                sensor_id,
                "T2",
                TEMP_CELSIUS,
                "mdi:arrow-left-bold-outline",
                "Temp. Ritorno",
            )
        )
        # T1 Idro
        entity_list.append(
            SensorX(
                sensor_id,
                "T1",
                TEMP_CELSIUS,
                None,
                code_status.get(
                    _config["value_descrizione_sonda_t1_idro"],
                    _config["value_descrizione_sonda_t1_idro"],
                ),
            )
        )

    # Quantità pellet
    entity_list.append(
        SensorX(
            sensor_id,
            "PQT",
            "kg",
            "mdi:chart-bell-curve-cumulative",
            "Pellet Consumato",
        )
    )

    # da rimpiazzare con flag presenza sonda livello pellet tipo leveltronic
    if _config["flag_presenza_luci"]:
        entity_list.append(SensorPelletL(sensor_id))

    add_entities(
        entity_list,
        update_before_add=True,
    )


class SensorX(Entity):
    """Representation of a sensor."""

    def __init__(self, class_id, key_val, unit=None, icon=None, friendly_name=None):
        """Initialize the sensor."""
        self._state = None
        self._id = class_id
        self._unit = unit
        self._key = key_val
        self._icon = icon
        self._fname = friendly_name

        self.DATA_DOMAIN = DATA_PALAZZETTI + self._id

    # @property
    # def name(self):
    #    """Return the name of the sensor."""
    #    return self._id + "_" + self._key.lower()

    @property
    def unique_id(self):
        """Return the name of the sensor."""
        return self._id + "_" + self._key

    # @property
    # def friendly_name(self):
    #    """Return the name of the sensor."""
    #    return self._fname

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    # @property
    # def unit_of_measurement(self):
    #    """Return the unit of measurement."""
    #    return self._unit

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._id)},
            "name": self.hass.data[self.DATA_DOMAIN].get_key("LABEL"),
            "manufacturer": "Palazzetti Lelio S.p.A.",
            "model": self.hass.data[self.DATA_DOMAIN].get_key("SN"),
            "sw_version": self.hass.data[self.DATA_DOMAIN].get_key("SYSTEM"),
        }

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        # self._state = self.hass.data[DOMAIN]['t1']
        self._state = self.hass.data[self.DATA_DOMAIN].get_key(self._key)

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        # attributes = super().device_state_attributes
        attributes = json.loads("{}")
        attributes.update(
            {
                ATTR_FRIENDLY_NAME: self._fname,
                ATTR_UNIT_OF_MEASUREMENT: self._unit,
                "test": "test string",
            }
        )
        return attributes


class SensorPelletL(Entity):
    """Representation of a sensor."""

    def __init__(self, class_id):
        """Initialize the sensor."""
        self._state = None
        self._id = class_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._id + "_pellet_l"

    @property
    def friendly_name(self):
        """Return the name of the sensor."""
        return "Pellet level"

    @property
    def icon(self):
        """Return the name of the sensor."""
        return "mdi:cup"

    @property
    def unique_id(self):
        """Return the name of the sensor."""
        return self._id + "_PLEVEL"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "cm"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._id)},
            "name": self.hass.data[DATA_PALAZZETTI + self._id].get_key("LABEL"),
            "manufacturer": "Palazzetti Lelio S.p.A.",
            "model": self.hass.data[DATA_PALAZZETTI + self._id].get_key("SN"),
            "sw_version": self.hass.data[DATA_PALAZZETTI + self._id].get_key("SYSTEM"),
        }

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        # self._state = self.hass.data[DOMAIN]['plevel']
        self._state = self.hass.data[DATA_PALAZZETTI + self._id].get_key("PLEVEL")
