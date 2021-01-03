"""Config flow for warmup4ie integration."""
import logging
import socket
import json
import voluptuous as vol

from homeassistant import config_entries, core, exceptions

from . import DOMAIN  # pylint:disable=unused-import

_LOGGER = logging.getLogger(__name__)

# TODO adjust the data schema to the data that you need
DATA_SCHEMA = vol.Schema({"host": str})

async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to connect.
    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    # Enable broadcasting mode
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    server.settimeout(3)
    mymess=""
    message = b"plzbridge?"
    _LOGGER.error("try to connect to at %s", data)
    for i in range(0,3):
      sequence_number = i
      server.sendto(message, (data, 54549))
      #server.sendto(message, ('<broadcast>', 54549))
      # Receive the client packet along with the address it is coming from
      try:
        data, addr = server.recvfrom(1024)
        if data != '':
          mymess=data.decode('utf-8')
          mymess_json=json.loads(mymess)
          _LOGGER.error("the macaddress is %s", mymess_json["DATA"]["MAC"])
          return mymess_json["DATA"]["LABEL"]
          break
      except socket.timeout:
          pass
    
    raise CannotConnect()

async def validate_input2(hass: core.HomeAssistant, mydata):
    """Validate the user input allows us to connect.
    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    from .palazzetti_local_api import Palazzetti

    class Object(object):
        pass

    a = Object()
    a.data={}
    a.data["host"]=mydata

    try:
        test_api = Palazzetti(hass, a,'test')
        result = await test_api.async_test()
        #_LOGGER.error("the ConnBox label is %s", result)
        #if result is None:
        #    raise CannotConnect()
        #else:
        return result
        #return 
    except:
        _LOGGER.error("couldn't find a ConnBox at %s", mydata)
        del a
        del test_api
        raise CannotConnect()

class DomainConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Palazzetti."""

    VERSION = 1

    CONNECTION_CLASS = config_entries.CONN_CLASS_UNKNOWN


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
            self.host = user_input['host']
            return await self.async_step_link(user_input)

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA
        )
    
    async def async_step_link(self, user_input=None):
        """Attempt to link with ConnBox"""
        errors = {}

        try:
            info = await validate_input2(self.hass, self.host)
            print(info)
            return self.async_create_entry(title = "ConnBox ("+self.host+")" , data = user_input)

        except CannotConnect:
            _LOGGER.error("Error connecting to the ConnBox at %s", self.host)
            errors['base'] = 'cannot_connect'
            return self.async_abort(
                reason='cannot_connect'
            )

        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unknown error connecting to the ConnBox at %s", self.host)
            errors['base'] = 'unknown'

        # If there was no user input, do not show the errors.
        # if user_input is None:
        #     errors = {}

        """
        return self.async_show_form(
            step_id='link',
            errors=errors,
        )"""

class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""
