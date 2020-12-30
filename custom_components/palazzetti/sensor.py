"""Platform for sensor integration."""
from homeassistant.const import (TEMP_CELSIUS, ATTR_UNIT_OF_MEASUREMENT, ATTR_FRIENDLY_NAME)
from homeassistant.helpers.entity import Entity

from . import DOMAIN

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    # We only want this platform to be set up via discovery.
    if discovery_info is None:
        return
    add_entities([SensorT1(),SensorT2(),SensorT5(),SensorSETP(),SensorPelletL(),SensorPelletQ()])


class SensorT1(Entity):
    """Representation of a sensor."""

    def __init__(self):
        """Initialize the sensor."""
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return DOMAIN + '_t1'

    @property
    def unique_id(self):
        """Return the name of the sensor."""
        return DOMAIN + '_T1'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = self.hass.data[DOMAIN]['t1']

class SensorT2(Entity):
    """Representation of a sensor."""

    def __init__(self):
        """Initialize the sensor."""
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return DOMAIN + '_t2'

    @property
    def unique_id(self):
        """Return the name of the sensor."""
        return DOMAIN + '_T2'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = self.hass.data[DOMAIN]['t2']

class SensorT5(Entity):
    """Representation of a sensor."""

    def __init__(self):
        """Initialize the sensor."""
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return DOMAIN + '_t5'

    @property
    def unique_id(self):
        """Return the name of the sensor."""
        return DOMAIN + '_T5'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = self.hass.data[DOMAIN]['t5']

class SensorSETP(Entity):
    """Representation of a sensor."""

    def __init__(self):
        """Initialize the sensor."""
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return DOMAIN + '_setp'

    @property
    def unique_id(self):
        """Return the name of the sensor."""
        return DOMAIN + '_SETP'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = self.hass.data[DOMAIN]['setp']

class SensorPelletQ(Entity):
    """Representation of a sensor."""

    def __init__(self):
        """Initialize the sensor."""
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return DOMAIN + '_pellet_q'
    
    @property
    def friendly_name(self):
        """Return the name of the sensor."""
        return 'Pellet counter'
    
    @property
    def icon(self):
        """Return the name of the sensor."""
        return 'mdi:chart-bell-curve-cumulative'

    @property
    def unique_id(self):
        """Return the name of the sensor."""
        return DOMAIN + '_PQTY'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return 'kg'

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = self.hass.data[DOMAIN]['pellet']

class SensorPelletL(Entity):
    """Representation of a sensor."""

    def __init__(self):
        """Initialize the sensor."""
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return DOMAIN + '_pellet_l'
    
    @property
    def friendly_name(self):
        """Return the name of the sensor."""
        return 'Pellet level'
    
    @property
    def icon(self):
        """Return the name of the sensor."""
        return 'mdi:cup'

    @property
    def unique_id(self):
        """Return the name of the sensor."""
        return DOMAIN + '_PLEVEL'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return 'cm'

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = self.hass.data[DOMAIN]['plevel']
