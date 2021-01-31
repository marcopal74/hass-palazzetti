"""Demo fan platform that has a fake fan."""
from homeassistant.components.fan import (
    SPEED_HIGH,
    SPEED_LOW,
    SPEED_MEDIUM,
    SUPPORT_DIRECTION,
    SUPPORT_OSCILLATE,
    SUPPORT_SET_SPEED,
    FanEntity,
)
from homeassistant.const import STATE_OFF

from .const import DOMAIN, DATA_PALAZZETTI

FULL_SUPPORT = SUPPORT_SET_SPEED | SUPPORT_OSCILLATE | SUPPORT_DIRECTION
LIMITED_SUPPORT = SUPPORT_SET_SPEED


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Demo config entry."""
    product = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        [
            DemoFan(hass, product, "fan1", "Fan", LIMITED_SUPPORT),
            # DemoFan(hass, fan_id, "fan2", "Posteriore SX", LIMITED_SUPPORT),
            # DemoFan(hass, fan_id, "fan3", "Posteriore DX", LIMITED_SUPPORT),
        ]
    )


class DemoFan(FanEntity):
    """A demonstration fan component."""

    def __init__(
        self, hass, product, fan_id, name: str, supported_features: int
    ) -> None:
        """Initialize the entity."""
        self.hass = hass
        self._id = product.product_id
        self._product = product
        self._unique_id = self._id + "_" + fan_id
        self._supported_features = supported_features
        self._speed = STATE_OFF
        self._oscillating = None
        self._direction = None
        self._name = name

        self.DATA_DOMAIN = DATA_PALAZZETTI + self._id

    @property
    def unique_id(self):
        """Return the unique id."""
        return self._unique_id

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._id)},
            # "name": self._product.get_key("LABEL"),
            # "manufacturer": "Palazzetti Lelio S.p.A.",
            # "model": self._product.get_key("SN"),
            # "sw_version": "mod: "
            # + str(self._product.get_key("MOD"))
            # + " v"
            # + str(self._product.get_key("VER"))
            # + " "
            # + self._product.get_key("FWDATE"),
            # "via_device": (DOMAIN, self._product.hub_id),
        }

    @property
    def name(self) -> str:
        """Get entity name."""
        return self._name

    @property
    def should_poll(self):
        """No polling needed for a demo fan."""
        return True

    @property
    def speed(self) -> str:
        """Return the current speed."""
        return self._speed

    @property
    def speed_list(self) -> list:
        """Get the list of available speeds."""
        return [STATE_OFF, SPEED_LOW, SPEED_MEDIUM, SPEED_HIGH]

    def turn_on(self, speed: str = None, **kwargs) -> None:
        """Turn on the entity."""
        if speed is None:
            speed = SPEED_MEDIUM
        self.set_speed(speed)

    def turn_off(self, **kwargs) -> None:
        """Turn off the entity."""
        self.oscillate(False)
        self.set_speed(STATE_OFF)

    def set_speed(self, speed: str) -> None:
        """Set the speed of the fan."""
        self._speed = speed
        self.schedule_update_ha_state()

    def set_direction(self, direction: str) -> None:
        """Set the direction of the fan."""
        self._direction = direction
        self.schedule_update_ha_state()

    def oscillate(self, oscillating: bool) -> None:
        """Set oscillation."""
        self._oscillating = oscillating
        self.schedule_update_ha_state()

    @property
    def current_direction(self) -> str:
        """Fan direction."""
        return self._direction

    @property
    def oscillating(self) -> bool:
        """Oscillating."""
        return self._oscillating

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return self._supported_features
