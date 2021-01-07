"""Config flow for warmup4ie integration."""
import logging
import json
import voluptuous as vol
from .palazzetti_local_api import Palazzetti

from homeassistant import config_entries, core, exceptions

from . import DOMAIN  # pylint:disable=unused-import

_LOGGER = logging.getLogger(__name__)

# TODO adjust the data schema to the data that you need
DATA_SCHEMA = vol.Schema({"host": str})


async def validate_input(hass: core.HomeAssistant, mydata):
    """Validate the user input allows us to connect.
    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    from .palazzetti_local_api import PalDiscovery

    check_api = PalDiscovery()
    check_ip = await check_api.checkIP(mydata)
    if check_ip:
        # IP is a Connection Box

        # get static data
        myapi = Palazzetti(mydata)
        await myapi.async_get_stdt()
        await myapi.async_config_parse()
        response = myapi.get_data_config()
        return response
    return False


class DomainConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Palazzetti."""

    VERSION = 1

    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        # errors = {}
        # errors["base"] = "cannot_connect"
        # if user_input is not None:
        #     try:
        #         info = await validate_input(self.hass, user_input)
        #         return self.async_create_entry(title = "ConnBox IP: " + user_input["host"] , data = user_input)
        #     except CannotConnect:
        #         errors["base"] = "cannot_connect"
        #     except InvalidAuth:
        #         errors["base"] = "invalid_auth"
        #     except Exception:  # pylint: disable=broad-except
        #         _LOGGER.exception("Unexpected exception")
        #         errors["base"] = "unknown"
        if user_input is not None:

            check_exists = await self.async_set_unique_id(
                "plz_" + user_input["host"].replace(".", "")
            )
            if check_exists:
                return self.async_abort(reason="host_exists")

            self.host = user_input["host"]
            return await self.async_step_link(user_input)

        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)

    async def async_step_link(self, user_input=None):
        """Attempt to link with ConnBox"""
        errors = {}

        try:
            info = await validate_input(self.hass, self.host)
            user_input["stove"] = info
            if info:
                return self.async_create_entry(
                    title="ConnBox (" + self.host + ")",
                    data=user_input
                    # version=self.VERSION,
                    # connection_class=self.CONNECTION_CLASS,
                )

        except CannotConnect:
            _LOGGER.error("Error connecting to the ConnBox at %s", self.host)
            errors["base"] = "cannot_connect"

        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception(
                "Unknown error connecting to the ConnBox at %s", self.host
            )
            errors["base"] = "unknown"

        return self.async_abort(reason="cannot_connect")


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""
