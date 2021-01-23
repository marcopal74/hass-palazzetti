"""Platform for sensor integration."""
import json
from homeassistant.const import (
    TEMP_CELSIUS,
    ATTR_UNIT_OF_MEASUREMENT,
    ATTR_FRIENDLY_NAME,
    DEVICE_DEFAULT_NAME,
)

from homeassistant.helpers.entity import Entity

from .const import DOMAIN, DATA_PALAZZETTI

from .helper import get_platform, MyNumber


async def create_input_number(hass, config_entry, product):
    platform_name = "input_number"

    my_sliders = []

    # slider impostazione potenza
    data = {
        "id": f"{config_entry.unique_id}_pwr",
        "initial": product.get_data_config_json()["_value_power"],
        "max": 5.0,
        "min": 1.0,
        "mode": "slider",
        "name": "Potenza",
        "step": 1.0,
        "icon": "mdi:fire",
    }
    slider_power = MyNumber(hass, data, product, "power")
    my_sliders.append(slider_power)

    # slider impostazione setpoint
    if product.get_data_config_json()["_flag_has_setpoint"]:
        data2 = {
            "id": f"{config_entry.unique_id}_setpoint",
            "initial": product.get_data_config_json()["_value_setpoint"],
            "max": product.get_data_config_json()["_value_setpoint_max"],
            "min": product.get_data_config_json()["_value_setpoint_min"],
            "mode": "slider",
            "name": "Setpoint",
            "unit_of_measurement": "°C",
            "step": 1.0,
            "icon": "hass:thermometer",
        }
        slider_setpoint = MyNumber(hass, data2, product, "setpoint")
        my_sliders.append(slider_setpoint)

    if product.get_data_config_json()["_flag_has_fan_main"]:
        fan = 1
        data3 = {
            "id": f"{config_entry.unique_id}_fan1",
            "initial": product.get_data_config_json()["_value_fan_main"],
            "max": product.get_data_config_json()["_value_fan_limits"][
                (((fan - 1) * 2) + 1)
            ],
            "min": product.get_data_config_json()["_value_fan_limits"][((fan - 1) * 2)],
            "mode": "slider",
            "name": "Main Fan",
            "step": 1.0,
            "icon": "mdi:fan",
        }
        slider_fan1 = MyNumber(hass, data3, product, "fan1")
        my_sliders.append(slider_fan1)

    if product.get_data_config_json()["_flag_has_fan_second"]:
        fan = 2
        data4 = {
            "id": f"{config_entry.unique_id}_fan2",
            "initial": product.get_data_config_json()["_value_fan_second"],
            "max": product.get_data_config_json()["_value_fan_limits"][
                (((fan - 1) * 2) + 1)
            ],
            "min": product.get_data_config_json()["_value_fan_limits"][((fan - 1) * 2)],
            "mode": "slider",
            "name": "Fan 2",
            "step": 1.0,
            "icon": "mdi:fan-speed-2",
        }
        slider_fan2 = MyNumber(hass, data4, product, "fan2")
        my_sliders.append(slider_fan2)

    if product.get_data_config_json()["_flag_has_fan_third"]:
        fan = 3
        data5 = {
            "id": f"{config_entry.unique_id}_fan3",
            "initial": product.get_data_config_json()["_value_fan_third"],
            "max": product.get_data_config_json()["_value_fan_limits"][
                (((fan - 1) * 2) + 1)
            ],
            "min": product.get_data_config_json()["_value_fan_limits"][((fan - 1) * 2)],
            "mode": "slider",
            "name": "Fan 3",
            "step": 1.0,
            "icon": "mdi:fan-speed-3",
        }
        slider_fan3 = MyNumber(hass, data5, product, "fan3")
        my_sliders.append(slider_fan3)

    # if no sliders exit
    if not my_sliders:
        return

    input_number_platform = get_platform(hass, platform_name)
    # aggiungo la config_entry alla platform così posso agganciarla ai device
    input_number_platform.config_entry = config_entry

    await input_number_platform.async_add_entities(my_sliders, True)


async def async_setup_entry(hass, config_entry, add_entities):
    """Set up the sensor platform from config flow"""
    product = hass.data[DOMAIN][config_entry.entry_id]
    await create_input_number(hass, config_entry, product)

    _config = product.get_data_config_json()

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
    add_entities(
        entity_list,
        update_before_add=True,
    )


class SensorX(Entity):
    """Representation of a sensor."""

    def __init__(self, product, key_val, unit=None, icon=None, friendly_name=None):
        """Initialize the sensor."""
        self._product = product
        self._state = None
        self._id = product.product_id
        self._unit = unit
        self._key = key_val
        self._icon = icon
        self._fname = friendly_name or DEVICE_DEFAULT_NAME

        self.DATA_DOMAIN = DATA_PALAZZETTI + self._id

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._fname

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
    def available(self) -> bool:
        """Return True if the product is available."""
        return self._product.online

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._id)},
            "name": self._product.get_key("LABEL"),
            "manufacturer": "Palazzetti Lelio S.p.A.",
            "model": self._product.get_key("SN"),
            "sw_version": self._product.get_key("SYSTEM"),
        }

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = self._product.get_key(self._key)

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        # attributes = super().device_state_attributes
        attributes = json.loads("{}")
        attributes.update(
            {
                # "name": self._id + "_" + self._key.lower(),
                # ATTR_FRIENDLY_NAME: self._fname,
                ATTR_UNIT_OF_MEASUREMENT: self._unit,
            }
        )
        return attributes
