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

    nome_temp = code_status.get(
        _config["_value_temp_air_description"],
        _config["_value_temp_air_description"],
    )
    if _config["_flag_is_hydro"]:
        nome_temp = code_status.get(
            _config["_value_temp_hydro_description"],
            _config["_value_temp_hydro_description"],
        )

    # Sonda principale
    entity_list.append(
        SensorX(
            sensor_id,
            _config["_value_temp_main_description"],
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

    if _config["_flag_is_hydro"]:
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
                "mdi:arrow-right-bold",
                code_status.get(
                    _config["_value_temp_hydro_t1_description"],
                    _config["_value_temp_hydro_t1_description"],
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

    # Leveltronic
    if _config["_flag_has_pellet_sensor_leveltronic"]:
        entity_list.append(
            SensorX(
                sensor_id,
                "PLEVEL",
                "cm",
                "mdi:cup",
                "Livello Pellet",
            )
        )

    # Now creates the proper sensor entities
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

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Return the name of the sensor."""
        return self._icon

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
                "credits": "Palazzetti",
            }
        )
        return attributes
