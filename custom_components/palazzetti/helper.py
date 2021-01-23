from asyncio import gather
import voluptuous as vol
from homeassistant import bootstrap
from homeassistant.helpers.entity_platform import async_get_platforms
from homeassistant.components.input_number import InputNumber

from .const import DOMAIN, DATA_PALAZZETTI


def get_platform(hass, name):
    platform_list = async_get_platforms(hass, name)

    for platform in platform_list:
        if platform.domain == name:
            return platform

    return None


def create_platform(hass, name):
    gather(bootstrap.async_setup_component(hass, name, {}))


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
