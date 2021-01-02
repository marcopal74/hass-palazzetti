"""
The "palazzetti" custom component.
Configuration:
To use the palazzetti component you will need to add the integration from 
the integration menu and set the ip of the Connection Box when asked
"""
import logging, asyncio, json, requests, voluptuous, aiohttp
#from datetime import timedelta

from homeassistant import config_entries, core

from .const import (DOMAIN,DATA_PALAZZETTI,INTERVAL,INTERVAL_CNTR,INTERVAL_STDT)

from .palazzetti_local_api import Palazzetti

from homeassistant.helpers.event import async_track_time_interval
import homeassistant.helpers.config_validation as cv

import time

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = voluptuous.Schema({
    DOMAIN: voluptuous.Schema({
      voluptuous.Required('ip'): cv.string,
    })
}, extra=voluptuous.ALLOW_EXTRA)

async def async_setup_entry(hass: core.HomeAssistant, entry: config_entries.ConfigEntry):
    _LOGGER.debug("Init of palazzetti component")
    
    #to be used to define unique id for instance
    #IP = entry.data["host"].replace(".","")
    
    #to store data for sensor platform
    hass.data[DOMAIN] = {
      't1': 0,
      't2': 0,
      't5': 0,
      'setp': 0,
      'plevel': 0,
      'pellet': 0
    }
    
    api = Palazzetti(hass, entry.data["host"])
    hass.data[DATA_PALAZZETTI] = api
    await api.async_get_stdt()
    await api.async_get_alls()
    await api.async_get_cntr()

    # loop for get state of stove
    def update_state_datas(event_time):
        return asyncio.run_coroutine_threadsafe( api.async_get_alls(), hass.loop)

    # loop for get counter of stove
    def update_cntr_datas(event_time):
        return asyncio.run_coroutine_threadsafe( api.async_get_cntr(), hass.loop)

    # loop for get static data of stove
    def update_static_datas(event_time):
        return asyncio.run_coroutine_threadsafe( api.async_get_stdt(), hass.loop)

    async_track_time_interval(hass, update_state_datas, INTERVAL)
    async_track_time_interval(hass, update_cntr_datas, INTERVAL_CNTR)
    async_track_time_interval(hass, update_static_datas, INTERVAL_STDT)

    #sensor platform
    hass.async_add_job(
        hass.config_entries.async_forward_entry_setup(entry, 'sensor')
    )
    
    # services
    def set_parameters(call):
        """Handle the service call 'set'"""
        api.set_parameters(call.data)

    hass.services.async_register(DOMAIN, 'set_parms', set_parameters)

    # Return boolean to indicate that initialization was successfully.
    return True

async def async_setup(hass, config):
    """Set up the GitHub Custom component from yaml configuration."""
    return True