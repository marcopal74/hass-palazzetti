"""Demo platform for the cover component."""
from homeassistant.components.cover import (
    SUPPORT_CLOSE,
    SUPPORT_OPEN,
    CoverEntity,
)

# from homeassistant.core import callback
# from homeassistant.helpers.event import async_track_utc_time_change

from .const import DOMAIN


async def async_setup_entry(hass, config_entry, async_add_entities):
    product = hass.data[DOMAIN][config_entry.entry_id]
    myposition = product.get_key("DOOR")
    hassposition = 0
    if myposition == 3:
        hassposition = 0
    elif myposition == 4:
        hassposition = 100

    """Set up the Demo covers."""
    async_add_entities(
        [
            PalCover(
                hass,
                product,
                "fdoor",
                "Fire Door",
                position=hassposition,
                device_class="door",
                supported_features=(SUPPORT_OPEN | SUPPORT_CLOSE),
            ),
        ]
    )


class PalCover(CoverEntity):
    """Representation of a demo cover."""

    def __init__(
        self,
        hass,
        product,
        door_id,
        name,
        position=None,
        tilt_position=None,
        device_class=None,
        supported_features=None,
    ):
        """Initialize the cover."""
        self.hass = hass
        self._id = product.product_id
        self._product = product
        self._unique_id = self._id + "_" + door_id
        self._name = name
        self._position = position
        self._device_class = device_class
        self._supported_features = supported_features
        self._set_position = None
        self._set_tilt_position = None
        self._tilt_position = tilt_position
        self._requested_closing = True
        self._requested_closing_tilt = True
        self._unsub_listener_cover = None
        self._unsub_listener_cover_tilt = None
        self._is_opening = False
        self._is_closing = False

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._id)},
        }

    @property
    def available(self) -> bool:
        """Return True if roller and hub is available."""
        return self._product.online

    @property
    def unique_id(self):
        """Return unique ID for cover."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the cover."""
        return self._name

    @property
    def should_poll(self):
        """No polling needed for a demo cover."""
        return True

    @property
    def current_cover_position(self):
        """Return the current position of the cover."""
        myposition = self._product.get_key("DOOR")
        hassposition = 0
        if myposition == 3:
            hassposition = 0
            self._is_closing = False
            self._is_opening = False
        elif myposition == 4:
            hassposition = 100
            self._is_closing = False
            self._is_opening = False
        self._position = hassposition
        return self._position

    @property
    def is_closed(self):
        """Return if the cover is closed."""
        return self._product.get_key("DOOR") == 3

    @property
    def is_closing(self):
        """Return if the cover is closing."""
        return self._is_closing

    @property
    def is_opening(self):
        """Return if the cover is opening."""
        return self._is_opening

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return self._device_class

    @property
    def supported_features(self):
        """Flag supported features."""
        if self._supported_features is not None:
            return self._supported_features
        # return super().supported_features

    async def async_close_cover(self, **kwargs):
        """Close the cover."""
        if self._position == 0:
            return
        await self._product.async_set_door(False)

        self._is_closing = True
        self.async_write_ha_state()

    async def async_open_cover(self, **kwargs):
        """Open the cover."""
        if self._position == 100:
            return
        await self._product.async_set_door(True)

        self._is_opening = True
        self.async_write_ha_state()
