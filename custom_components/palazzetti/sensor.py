"""Platform for sensor integration."""
from homeassistant.const import (TEMP_CELSIUS, ATTR_UNIT_OF_MEASUREMENT, ATTR_FRIENDLY_NAME)
from homeassistant.helpers.entity import Entity

from .const import (DOMAIN,DATA_PALAZZETTI)

async def async_setup_entry(hass, config_entry, add_entities):
    """Set up the sensor platform from config flow"""
    #ipname=config_entry.replace(".","")
    setup_platform(hass,config_entry,add_entities)
    
def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform from configuration.yaml"""
    add_entities([SensorT1(),SensorT2(),SensorT5(),SensorSETP(),SensorPelletL(),SensorPelletQ()], update_before_add=True)


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
        #self._state = self.hass.data[DOMAIN]['t1']
        self._state = self.hass.data[DATA_PALAZZETTI].get_key('T1')

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
        self._state = self.hass.data[DATA_PALAZZETTI].get_key('T2')

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
        #self._state = self.hass.data[DOMAIN]['t5']
        self._state = self.hass.data[DATA_PALAZZETTI].get_key('T5')

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
        #self._state = self.hass.data[DOMAIN]['setp']
        self._state = self.hass.data[DATA_PALAZZETTI].get_key('SETP')

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
        return DOMAIN + '_PQT'

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
        #self._state = self.hass.data[DOMAIN]['pellet']
        self._state = self.hass.data[DATA_PALAZZETTI].get_key('PQT')

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
        #self._state = self.hass.data[DOMAIN]['plevel']
        self._state = self.hass.data[DATA_PALAZZETTI].get_key('PLEVEL')
