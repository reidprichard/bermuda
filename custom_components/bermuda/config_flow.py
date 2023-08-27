"""Adds config flow for Bermuda BLE Trilateration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.core import callback
from homeassistant.helpers.config_entry_flow import FlowResult

from .const import CONF_DEVTRACK_TIMEOUT
from .const import CONF_MAX_RADIUS
from .const import DOMAIN
from .const import NAME

# from homeassistant import data_entry_flow

# from homeassistant.helpers.aiohttp_client import async_create_clientsession


class BermudaFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for bermuda."""

    VERSION = 1
    # CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> FlowResult:
        """Support automatic initiation of setup through bluetooth discovery.
        (we still how a confirmation form to the user, though)
        This is triggered by discovery matchers set in manifest.json,
        and since we track any BLE advert, we're being a little cheeky by listing any.
        """
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        # Create a unique ID so that we don't get multiple discoveries appearing.
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        return self.async_show_form(step_id="user", description_placeholders=NAME)

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user.

        We don't need any config for base setup, so we just activate
        (but only for one instance)
        """

        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            # create the integration!
            return self.async_create_entry(
                title=NAME, data={"source": "user"}, description=NAME
            )

        return self.async_show_form(step_id="user", description_placeholders=NAME)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return BermudaOptionsFlowHandler(config_entry)

    # async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
    #     """Show the configuration form to edit location data."""
    #     return self.async_show_form(
    #         step_id="user",
    #         data_schema=vol.Schema(
    #             {vol.Required(CONF_USERNAME): str, vol.Required(CONF_PASSWORD): str}
    #         ),
    #         errors=self._errors,
    #     )


class BermudaOptionsFlowHandler(config_entries.OptionsFlow):
    """Config flow options handler for bermuda."""

    def __init__(self, config_entry):
        """Initialize HACS options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        """Manage the options."""
        return await self.async_step_globalopts()

    async def async_step_globalopts(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()

        return self.async_show_form(
            step_id="globalopts",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_MAX_RADIUS,
                        default=self.options.get(CONF_MAX_RADIUS, 3.0),
                    ): float,
                    vol.Required(
                        CONF_DEVTRACK_TIMEOUT,
                        default=self.options.get(CONF_DEVTRACK_TIMEOUT, 30),
                    ): int,
                }
            ),
        )

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(title=NAME, data=self.options)
