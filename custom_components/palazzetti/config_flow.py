"""Config flow for warmup4ie integration."""
import logging
import json
import re
import voluptuous as vol
from .palazzetti_sdk_local_api import Palazzetti

from homeassistant import config_entries, core, exceptions

from . import DOMAIN  # pylint:disable=unused-import

_LOGGER = logging.getLogger(__name__)

# TODO adjust the data schema to the data that you need
DATA_SCHEMA = vol.Schema({"host": str})


async def validate_input(_user_host):
    """chech if user host is a ConnectionBox IP"""
    from .palazzetti_sdk_local_api import PalDiscovery

    check_api = PalDiscovery()
    check_ip = await check_api.checkIP(_user_host)

    if check_ip:
        myconfig = {}
        print("check-ip is OK")
        # IP is a Connection Box

        # get static data
        myapi = Palazzetti(_user_host)
        print("object is created")
        await myapi.async_get_stdt()
        # await myapi.async_get_alls()

        myconfig["config"] = myapi.get_data_config_json()
        myconfig["data"] = myapi.get_data_json()

        if "SN" in myconfig["data"]:
            _sn = myconfig["data"]["SN"]
            if re.search("[a-zA-Z]{2}[0-9]{7}[a-zA-Z0-9]{9}[0-9]{5}", _sn) == False:
                # _newsn = (
                #    "LT0000000"
                #    + str(_user_host).replace(".", "")
                #    + "00000000000000000000000"
                # )
                # await myapi.async_set_sn(_newsn[:23])
                # return false: SN not matching RegEx
                return False
        elif "MAC" in myconfig["data"]:
            _sn = "LT_" + myconfig["data"]["MAC"].replace(":", "")
        else:
            return False

        # return static data
        myconfig["data"].update({"SN": _sn})
        return myconfig

    # return false: IP not found
    return False


class DomainConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Palazzetti."""

    VERSION = 1

    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""

        if user_input is not None:

            self.host = user_input["host"]

            return await self.async_step_link(user_input)

        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)

    async def async_step_link(self, user_input=None):
        """Attempt to link with ConnBox"""
        errors = {}

        try:
            print("pre-validate input")
            info = await validate_input(self.host)
            if not info:
                return self.async_abort(reason="cannot_connect")

            user_input["stove"] = info["config"]
            print("post-validate input")
            if info["data"]["SN"]:
                # check if device is already registered using SN or LT_MAC if no SN available
                check_exists = await self.async_set_unique_id(
                    "plz_" + info["data"]["SN"].lower()
                )
                if check_exists:
                    return self.async_abort(reason="host_exists")

                return self.async_create_entry(
                    title=info["data"]["LABEL"],
                    data=user_input,
                    description="Descrizione a caso",
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
