"""
Device Registry

Registry for managing IoT devices.
Handles device registration, grouping, and status tracking.
"""

import uuid
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from backend.src.integrations.emqx.mqtt_types import (
    Device,
    DeviceGroup,
    ConnectionStatus,
    QoSLevel,
    DeviceActivity,
)


class DeviceRegistry:
    """
    Registry for IoT devices.
    
    Responsibilities:
    - Register devices
    - Group devices
    - Track status
    - Monitor heartbeats
    - Connection history
    """
    
    def __init__(self):
        # Device ID -> Device
        self._devices: Dict[str, Device] = {}
        # device_id (client) -> Device
        self._devices_by_client: Dict[str, Device] = {}
        # Group ID -> DeviceGroup
        self._groups: Dict[str, DeviceGroup] = {}
        # Device ID -> Group ID
        self._device_groups: Dict[str, str] = {}
        # Heartbeat tracking: device_id -> last_heartbeat
        self._heartbeats: Dict[str, datetime] = {}
    
    def register_device(
        self,
        device_id: str,
        name: str,
        device_type: str = "",
        group_id: Optional[str] = None,
        asset_id: Optional[str] = None,
        client_id: str = "",
        username: str = "",
        qos: QoSLevel = QoSLevel.QOS_0
    ) -> Device:
        """
        Register a new device.
        
        Args:
            device_id: Unique device ID
            name: Device name
            device_type: Device type
            group_id: Optional group ID
            asset_id: Optional linked asset ID
            client_id: MQTT client ID
            username: MQTT username
            qos: Default QoS level
            
        Returns:
            Created Device
        """
        device = Device(
            id=str(uuid.uuid4()),
            device_id=device_id,
            name=name,
            type=device_type,
            group_id=group_id,
            asset_id=asset_id,
            client_id=client_id,
            username=username,
            qos=qos,
            status=ConnectionStatus.DISCONNECTED
        )
        
        self._devices[device.id] = device
        self._devices_by_client[device_id] = device
        
        if group_id:
            self._device_groups[device.id] = group_id
        
        return device
    
    def get_device(self, device_id: str) -> Optional[Device]:
        """Get device by internal ID."""
        return self._devices.get(device_id)
    
    def get_device_by_client_id(self, client_id: str) -> Optional[Device]:
        """Get device by MQTT client ID."""
        return self._devices_by_client.get(client_id)
    
    def update_device(
        self,
        device: Device,
        **kwargs
    ) -> Device:
        """
        Update a device.
        
        Args:
            device: Device to update
            **kwargs: Fields to update
            
        Returns:
            Updated Device
        """
        for key, value in kwargs.items():
            if hasattr(device, key):
                setattr(device, key, value)
        
        device.updated_at = datetime.utcnow()
        return device
    
    def delete_device(self, device_id: str) -> bool:
        """
        Delete a device.
        
        Args:
            device_id: Internal device ID
            
        Returns:
            True if deleted
        """
        device = self._devices.get(device_id)
        if not device:
            return False
        
        # Remove from indices
        del self._devices[device_id]
        del self._devices_by_client[device.device_id]
        
        if device_id in self._device_groups:
            del self._device_groups[device_id]
        
        if device.device_id in self._heartbeats:
            del self._heartbeats[device.device_id]
        
        return True
    
    def connect_device(self, client_id: str) -> Optional[Device]:
        """
        Mark device as connected.
        
        Args:
            client_id: MQTT client ID
            
        Returns:
            Updated Device
        """
        device = self._devices_by_client.get(client_id)
        if device:
            device.status = ConnectionStatus.CONNECTED
            device.last_connected_at = datetime.utcnow()
            self._heartbeats[device.device_id] = datetime.utcnow()
        return device
    
    def disconnect_device(self, client_id: str) -> Optional[Device]:
        """
        Mark device as disconnected.
        
        Args:
            client_id: MQTT client ID
            
        Returns:
            Updated Device
        """
        device = self._devices_by_client.get(client_id)
        if device:
            device.status = ConnectionStatus.DISCONNECTED
            device.last_disconnected_at = datetime.utcnow()
        return device
    
    def record_message(self, client_id: str) -> Optional[Device]:
        """
        Record message received from device.
        
        Args:
            client_id: MQTT client ID
            
        Returns:
            Updated Device
        """
        device = self._devices_by_client.get(client_id)
        if device:
            device.last_message_at = datetime.utcnow()
        return device
    
    def heartbeat(self, client_id: str) -> Optional[Device]:
        """
        Record device heartbeat.
        
        Args:
            client_id: MQTT client ID
            
        Returns:
            Updated Device
        """
        device = self._devices_by_client.get(client_id)
        if device:
            self._heartbeats[device.device_id] = datetime.utcnow()
        return device
    
    def get_devices_by_group(self, group_id: str) -> List[Device]:
        """Get all devices in a group."""
        device_ids = [
            did for did, gid in self._device_groups.items()
            if gid == group_id
        ]
        return [self._devices[did] for did in device_ids if did in self._devices]
    
    def get_devices_by_asset(self, asset_id: str) -> List[Device]:
        """Get all devices linked to an asset."""
        return [d for d in self._devices.values() if d.asset_id == asset_id]
    
    def get_connected_devices(self) -> List[Device]:
        """Get all connected devices."""
        return [d for d in self._devices.values() if d.is_connected]
    
    def get_device_status(self, device_id: str) -> Dict:
        """Get device status summary."""
        device = self.get_device(device_id)
        if not device:
            return {}
        
        return {
            "device_id": device.device_id,
            "status": device.status.value,
            "activity": device.activity_status.value,
            "last_connected": device.last_connected_at.isoformat() if device.last_connected_at else None,
            "last_message": device.last_message_at.isoformat() if device.last_message_at else None,
        }
    
    def get_all_devices(
        self,
        connected_only: bool = False,
        group_id: Optional[str] = None
    ) -> List[Device]:
        """
        Get all devices.
        
        Args:
            connected_only: Only connected devices
            group_id: Filter by group
            
        Returns:
            List of devices
        """
        devices = list(self._devices.values())
        
        if connected_only:
            devices = [d for d in devices if d.is_connected]
        
        if group_id:
            devices = [d for d in devices if d.group_id == group_id]
        
        return devices
    
    def get_device_count(self) -> int:
        """Get total device count."""
        return len(self._devices)
    
    def get_connected_count(self) -> int:
        """Get connected device count."""
        return len([d for d in self._devices.values() if d.is_connected])
    
    # =========================================================================
    # Device Groups
    # =========================================================================
    
    def create_group(
        self,
        name: str,
        description: str = "",
        parent_group_id: Optional[str] = None
    ) -> DeviceGroup:
        """
        Create a device group.
        
        Args:
            name: Group name
            description: Group description
            parent_group_id: Optional parent group
            
        Returns:
            Created DeviceGroup
        """
        group = DeviceGroup(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            parent_group_id=parent_group_id
        )
        
        self._groups[group.id] = group
        return group
    
    def get_group(self, group_id: str) -> Optional[DeviceGroup]:
        """Get group by ID."""
        return self._groups.get(group_id)
    
    def get_all_groups(self) -> List[DeviceGroup]:
        """Get all groups."""
        return list(self._groups.values())
    
    def add_device_to_group(
        self,
        device_id: str,
        group_id: str
    ) -> bool:
        """Add device to group."""
        device = self._devices.get(device_id)
        group = self._groups.get(group_id)
        
        if not device or not group:
            return False
        
        device.group_id = group_id
        self._device_groups[device_id] = group_id
        return True
    
    def remove_device_from_group(self, device_id: str) -> bool:
        """Remove device from group."""
        if device_id in self._device_groups:
            del self._device_groups[device_id]
            device = self._devices.get(device_id)
            if device:
                device.group_id = None
            return True
        return False
    
    def get_group_device_count(self, group_id: str) -> int:
        """Get number of devices in group."""
        return len([did for did, gid in self._device_groups.items() if gid == group_id])
