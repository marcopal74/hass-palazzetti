"""Platform for sensor integration."""
from homeassistant.const import (
    TEMP_CELSIUS,
    ATTR_UNIT_OF_MEASUREMENT,
    DEVICE_DEFAULT_NAME,
)

from homeassistant.helpers.entity import Entity

from .const import DOMAIN


async def async_setup_entry(hass, config_entry, add_entities):
    """Set up the sensor platform from config flow"""
    myhub = hass.data[DOMAIN][config_entry.entry_id]
    product = myhub.product
    if not product.online:
        return

    _config = product.get_data_config_json()

    entity_list = []

    # logica di configurazione delle sonde in base al parse della configurazione
    code_status = {
        "kTemperaturaAmbiente": "Temp. Ambiente",
        "kTemperaturaAccumulo": "Temp. Accumulo",
        "kTemperaturaAcquaMandata": "Temp. Mandata",
    }

    nome_temp = code_status.get(
        _config["_value_temp_air_description"],
        _config["_value_temp_air_description"],
    )
    if _config["_flag_is_hydro"]:
        nome_temp = code_status.get(
            _config["_value_temp_hydro_description"],
            _config["_value_temp_hydro_description"],
        )

    # Label + status
    entity_list.append(
        SensorState(
            product,
            "status",
            None,
            product.get_key("LABEL"),
        )
    )

    # Sonda principale
    entity_list.append(
        SensorX(
            product,
            _config["_value_temp_main_description"],
            TEMP_CELSIUS,
            None,
            nome_temp,
        )
    )

    # Setpoint
    if _config["_flag_has_setpoint"]:
        entity_list.append(
            SensorX(
                product,
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
                product,
                "T2",
                TEMP_CELSIUS,
                "mdi:arrow-left-bold-outline",
                "Temp. Ritorno",
            )
        )
        # T1 Idro
        entity_list.append(
            SensorX(
                product,
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
    if _config["_flag_has_setpoint"]:
        entity_list.append(
            SensorX(
                product,
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
                product,
                "PLEVEL",
                "cm",
                "mdi:cup",
                "Livello Pellet",
            )
        )

    # Now creates the proper sensor entities
    add_entities(entity_list)
    # update_before_add=True,


class SensorX(Entity):
    """Representation of a sensor."""

    should_poll = False

    def __init__(self, product, key_val, unit=None, icon=None, friendly_name=None):
        """Initialize the sensor."""
        self._product = product
        self._key = key_val
        self._unit = unit
        self._icon = icon
        self._fname = friendly_name or DEVICE_DEFAULT_NAME

        # internal variables
        self._unique_id = "vuoto_" + self._key
        if product and product.product_id:
            self._unique_id = product.product_id + "_" + self._key

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._product.product_id)},
        }

    @property
    def unique_id(self):
        """Return the name of the sensor."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._fname

    @property
    def icon(self):
        """Return the name of the sensor."""
        return self._icon

    @property
    def available(self) -> bool:
        """Return True if the product is available."""
        return self._product.online

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._product.get_key(self._key)

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        # attributes = super().device_state_attributes
        attributes = {ATTR_UNIT_OF_MEASUREMENT: self._unit}
        return attributes

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

    async def async_update(self):
        print(f"sensorX Update: {self._key}")


class SensorState(Entity):
    """Representation of a sensor."""

    should_poll = False

    def __init__(self, product, key_val, unit=None, friendly_name=None):
        """Initialize the sensor."""
        self._product = product
        self._key = key_val
        self._unit = unit
        self._fname = friendly_name or DEVICE_DEFAULT_NAME

        # internal variables
        self._unique_id = "vuoto_" + self._key
        if product and product.product_id:
            self._unique_id = product.product_id + "_" + self._key

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._product.product_id)},
        }

    @property
    def unique_id(self):
        """Return the name of the sensor."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._fname

    @property
    def icon(self):
        """Return the name of the sensor."""
        status_icon = "mdi:fireplace-off"
        if self._product.get_key("STATUS") == 6:
            status_icon = "mdi:fireplace"
        elif self._product.get_data_config_json()["_flag_error_status"]:
            status_icon = "mdi:alert"

        return status_icon

    @property
    def available(self) -> bool:
        """Return True if the product is available."""
        return self._product.online

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._key in self._product.get_data_states():
            return self._product.get_data_states()[self._key]
        return "UNAVAILABLE"

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        # attributes = super().device_state_attributes
        _config_attrib = self._product.get_data_config_json()
        return _config_attrib

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

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        print("sensorState Update")
