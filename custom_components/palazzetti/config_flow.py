"""Config flow for warmup4ie integration."""
import logging
import re
import voluptuous as vol
from homeassistant import config_entries, exceptions
from .palazzetti_sdk_local_api import Palazzetti

from . import DOMAIN  # pylint:disable=unused-import

_LOGGER = logging.getLogger(__name__)

# TODO adjust the data schema to the data that you need
DATA_SCHEMA = vol.Schema({"host": str})
STEP_USER_DATA_SCHEMA = vol.Schema({"host": str})


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
        myconfig["hub_id"] = myapi.hub_id
        myconfig["hub_isbiocc"] = myapi.hub_isbiocc

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
                raise InvalidSN
        elif "MAC" in myconfig["data"]:
            _sn = "LT" + myconfig["data"]["MAC"].replace(":", "")
        else:
            raise InvalidSN

        # return static data
        myconfig["data"].update({"SN": _sn})
        return myconfig

    raise CannotConnect

    # return false: IP not found
    # return False


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

            user_input["stove"] = info["config"]
            user_input["hub_id"] = info["hub_id"]
            user_input["hub_isbiocc"] = info["hub_isbiocc"]
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
                    # description="Descrizione a caso",
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
