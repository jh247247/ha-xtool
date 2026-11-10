"""Isolated discovery-only X1 coordinator, without inherited WS controls."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from ...coordinator import XtoolCoordinator
from ..base import XtoolDeviceState
from .protocol_x1 import X1DiscoveryProtocol

if TYPE_CHECKING:
    from homeassistant.components.binary_sensor import BinarySensorEntity
    from homeassistant.components.sensor import SensorEntity


class X1DiscoveryCoordinator(XtoolCoordinator):
    """Publish only observed advertisement identity and reachability."""

    protocol: X1DiscoveryProtocol

    def __init__(
        self, hass: HomeAssistant, *, protocol: X1DiscoveryProtocol, **kwargs: Any,
    ) -> None:
        kwargs['enable_firmware_updates'] = False
        kwargs['scan_interval'] = max(int(kwargs.get('scan_interval', 60)), 60)
        super().__init__(hass, protocol=protocol, **kwargs)
        # DataUpdateCoordinator includes its name in outage logs; omit identifiers.
        self.name = 'xtool_x1_discovery'
        if self.serial_number:
            protocol.bind_serial(self.serial_number)

    async def _async_update_data(self) -> XtoolDeviceState:
        state = XtoolDeviceState()
        try:
            await self.protocol.poll_state(state)
        except (ConnectionError, OSError, TimeoutError) as err:
            raise UpdateFailed('X1 discovery unavailable or identity rejected') from err
        self.device_name = state.device_name
        self.serial_number = state.serial_number
        self.firmware_version = state.firmware_version
        return state

    def build_sensors(self) -> list[SensorEntity]:
        from .entities_x1 import X1IdentitySensor

        return [X1IdentitySensor(self, key, name) for key, name in (
            ('device_name', 'Advertised name'),
            ('firmware_version', 'Advertised firmware'),
            ('device_code', 'Advertised model code'),
            ('platform_version', 'Advertised platform'),
        )]

    def build_binary_sensors(self) -> list[BinarySensorEntity]:
        from .entities_x1 import X1DiscoveryReachable

        return [X1DiscoveryReachable(self)]
