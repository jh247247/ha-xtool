"""Only evidenced discovery information, never inferred machine state."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import EntityCategory

from ...entity import XtoolEntity

if TYPE_CHECKING:
    from .coordinator_x1 import X1DiscoveryCoordinator


class X1IdentitySensor(XtoolEntity, SensorEntity):
    """Read one advertised identity field while discovery is fresh."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    coordinator: X1DiscoveryCoordinator

    def __init__(self, coordinator: X1DiscoveryCoordinator, key: str, name: str) -> None:
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._set_unique_id('discovery_' + key)

    @property
    def native_value(self) -> str | None:
        device = self.coordinator.protocol.discovery
        if device is None:
            return None
        if self._key == 'device_name':
            return device.name
        if self._key == 'firmware_version':
            return device.version
        if self._key == 'device_code':
            return device.device_code
        return device.platform_version


class X1DiscoveryReachable(XtoolEntity, BinarySensorEntity):
    """An advertisement response is not proof that the machine is idle/safe."""

    _attr_name = 'Discovery reachable'
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: X1DiscoveryCoordinator) -> None:
        super().__init__(coordinator)
        self._set_unique_id('discovery_reachable')

    @property
    def available(self) -> bool:
        return True

    @property
    def is_on(self) -> bool:
        return bool(
            self.coordinator.last_update_success
            and self.coordinator.data
            and self.coordinator.data.available
        )
