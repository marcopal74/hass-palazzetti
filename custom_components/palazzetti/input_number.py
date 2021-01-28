from homeassistant.components.input_number import InputNumber
import voluptuous as vol
from .const import DOMAIN
from .helper import get_platform


async def create_input_number(hass, entry):
    product = hass.data[DOMAIN][entry.entry_id]
    my_sliders = []

    # slider impostazione potenza
    data = {
        "id": f"{entry.unique_id}_pwr",
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
            "id": f"{entry.unique_id}_setpoint",
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

    # slider impostazione ventilatore principale
    if product.get_data_config_json()["_flag_has_fan_main"]:
        fan = 1
        data3 = {
            "id": f"{entry.unique_id}_fan1",
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

    # slider impostazione secondo ventilatore
    if product.get_data_config_json()["_flag_has_fan_second"]:
        fan = 2
        data4 = {
            "id": f"{entry.unique_id}_fan2",
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

    # slider impostazione terzo ventilatore
    if product.get_data_config_json()["_flag_has_fan_third"]:
        fan = 3
        data5 = {
            "id": f"{entry.unique_id}_fan3",
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

    # apro la piattaforma degli slider: input_number
    platform_name = "input_number"
    input_number_platform = get_platform(hass, platform_name)
    # aggiungo la config_entry alla platform così posso agganciarla ai device
    input_number_platform.config_entry = entry

    # aggiunge gli slider alla platform caricata
    await input_number_platform.async_add_entities(my_sliders, True)


class MyNumber(InputNumber):
    """Representation of a slider."""

    def __init__(self, hass, config, product, tipo):
        """Initialize an input number."""
        super().__init__(config)
        self.hass = hass
        self._name = config.get("name")
        # self._id = self.unique_id[:-4]
        self._id = product.product_id
        self._product = product
        self._type = tipo

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def should_poll(self):
        """If entity should be polled."""
        return True

    @property
    def available(self) -> bool:
        """Return True if roller and hub is available."""
        return self._product.online

    @property
    def state(self):
        """Return the state of the component."""
        if self._type == "power":
            return self._product.get_key("PWR")
        elif self._type == "setpoint":
            return self._product.get_key("SETP")
        elif self._type == "fan1":
            return self._product.get_key("F2L")
        elif self._type == "fan2":
            return self._product.get_key("F2L")
        elif self._type == "fan3":
            return self._product.get_key("F2L")

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._id)},
            "name": self._product.get_key("LABEL"),
            "manufacturer": "Palazzetti Lelio S.p.A.",
            "model": self._product.get_key("SN"),
            "sw_version": self._product.get_key("SYSTEM"),
        }

    async def async_added_to_hass(self):
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        if self._current_value is not None:
            return

        state = await self.async_get_last_state()
        value = state and float(state.state)

        # Check against None because value can be 0
        if value is not None and self._minimum <= value <= self._maximum:
            self._current_value = value
        else:
            self._current_value = self._minimum

    async def async_set_value(self, value):
        """Set new value."""
        num_value = float(value)

        if num_value < self._minimum or num_value > self._maximum:
            raise vol.Invalid(
                f"Invalid value for {self.entity_id}: {value} (range {self._minimum} - {self._maximum})"
            )

        self._current_value = num_value
        if self._type == "power":
            await self._product.async_set_power(int(num_value))
        elif self._type == "setpoint":
            await self._product.async_set_setpoint(int(num_value))
        elif self._type == "fan1" or self._type == "fan2" or self._type == "fan3":
            await self._product.async_set_fan(int(self._type[-1:]), int(num_value))
        self.async_write_ha_state()

    async def async_increment(self):
        """Increment value."""
        await self.async_set_value(min(self._current_value + self._step, self._maximum))

    async def async_decrement(self):
        """Decrement value."""
        await self.async_set_value(max(self._current_value - self._step, self._minimum))
