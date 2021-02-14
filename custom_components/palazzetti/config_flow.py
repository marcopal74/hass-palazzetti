"""Config flow for warmup4ie integration."""
import logging
import re
import voluptuous as vol
from homeassistant import config_entries, exceptions
from .palazzetti_sdk_local_api import Hub

from . import DOMAIN  # pylint:disable=unused-import

_LOGGER = logging.getLogger(__name__)

# TODO adjust the data schema to the data that you need
DATA_SCHEMA = vol.Schema({"host": str})
STEP_USER_DATA_SCHEMA = vol.Schema({"host": str})


async def validate_input(_user_host):
    """chech if user host is a ConnectionBox IP"""

    myhub = Hub(_user_host)
    myconfig = {"hub_id": myhub.hub_id, "host": _user_host}

    await myhub.async_update()
    if myhub.online:
        myconfig["hub_isbiocc"] = myhub.hub_isbiocc
        myconfig["label"] = myhub.label
        return myconfig

    raise CannotConnect


class DomainConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Palazzetti."""

    VERSION = 1

    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            print("pre-validate input")
            self.host = user_input["host"]
            info = await validate_input(self.host)

            # user_input["stove"] = info["config"]
            user_input["hub_id"] = info["hub_id"]
            user_input["hub_isbiocc"] = info["hub_isbiocc"]
            print("post-validate input")
            check_exists = await self.async_set_unique_id(info["hub_id"].lower())

            if check_exists:
                return self.async_abort(reason="host_exists")

            return self.async_create_entry(
                title=info["label"],
                data=info,
            )

        except CannotConnect:
            _LOGGER.error("Error connecting to the ConnBox at %s", self.host)
            errors["base"] = "cannot_connect"

        except InvalidSN:
            _LOGGER.error("Error validating SN to the ConnBox at %s", self.host)
            errors["base"] = "invalid_sn"

        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception(
                "Unknown error connecting to the ConnBox at %s", self.host
            )
            errors["base"] = "unknown"

        # return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)
        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidSN(exceptions.HomeAssistantError):
    """Error indicating embedded SN is not valid"""
