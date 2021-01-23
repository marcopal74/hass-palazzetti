from homeassistant.components.input_number import InputNumber
import voluptuous as vol
from .const import DOMAIN
from .helper import get_platform, create_platform


async def create_input_number(hass, product, name, name_technical):
    input_number_name = "input_number"
    product.get_data_config_json()["_value_power"]
    data = {
        "id": f"{name_technical}_pwr",
        "initial": product.get_data_config_json()["_value_power"],
        "max": 5.0,
        "min": 1.0,
        "mode": "slider",
        "name": "Potenza",
        "step": 1.0,
        "icon": "mdi:fire",
    }

    input_number_platform = get_platform(hass, input_number_name)

    input_number = MyNumber(data)
    # input_number.entity_id = input_number_name + "." + name_technical

    await input_number_platform.async_add_entities([input_number], True)


async def async_setup_entry(hass, config_entry, add_entities):
    """Set up the sensor platform from config flow"""
    product = hass.data[DOMAIN][config_entry.entry_id]
    await create_input_number(hass, product, "test_in", config_entry.unique_id)


class MyNumber(InputNumber):
    """Representation of a slider."""

    def __init__(self, config, product):
        """Initialize an input number."""
        super().__init__(config)
        self._id = self.unique_id[:-4]
        self._product = product
        self.mydomain = DATA_PALAZZETTI + self._id

    @property
    def should_poll(self):
        """If entity should be polled."""
        return True

    @property
    def state(self):
        """Return the state of the component."""
        return self._product.get_key("PWR")

    @property
    def device_info(self):
        # self._id = self.unique_id[:-4]
        # self.mydomain = DATA_PALAZZETTI + self._id
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
        await self._product.async_set_power(int(num_value))
        self.async_write_ha_state()

    async def async_increment(self):
        """Increment value."""
        await self.async_set_value(min(self._current_value + self._step, self._maximum))

    async def async_decrement(self):
        """Decrement value."""
        await self.async_set_value(max(self._current_value - self._step, self._minimum))
