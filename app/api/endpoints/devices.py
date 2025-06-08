from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.device import Device, OS, UserDevice, Setup
from app.models.enums import OsTypes, PhoneBrands, AndroidUI

router = APIRouter()


class DeviceBase(BaseModel):
    """Base schema for device data"""
    device_name: str
    brand: PhoneBrands
    model: str
    os_id: int
    android_ui: Optional[AndroidUI] = None
    
    model_config = ConfigDict(from_attributes=True)


class DeviceCreate(DeviceBase):
    """Schema for creating a device"""
    pass


class DeviceResponse(DeviceBase):
    """Response schema for device"""
    id: int
    created_at: str
    updated_at: str


@router.get("/my-devices", response_model=List[Dict[str, Any]])
async def get_user_devices(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all devices registered to the current user"""
    
    # Get user devices with joined device and OS information
    user_devices = db.query(UserDevice).filter(UserDevice.user_id == current_user.id).all()
    
    result = []
    for user_device in user_devices:
        # Get device details
        device = db.query(Device).filter(Device.id == user_device.device_id).first()
        if not device:
            continue
            
        # Get OS details
        os_info = db.query(OS).filter(OS.id == device.os_id).first()
        
        result.append({
            "user_device_id": user_device.id,
            "device_id": device.id,
            "device_name": device.device_name,
            "brand": device.brand.value if device.brand else None,
            "model": device.model,
            "is_active": user_device.is_active,
            "registered_at": user_device.created_at.isoformat(),
            "os": {
                "id": os_info.id if os_info else None,
                "name": os_info.name if os_info else None,
                "version": os_info.version if os_info else None,
                "type": os_info.type.value if os_info and os_info.type else None
            },
            "android_ui": device.android_ui.value if device.android_ui else None
        })
    
    return result


@router.post("/register-device", status_code=status.HTTP_201_CREATED)
async def register_device(device_data: DeviceCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Register a new device for the current user"""
    
    # Check if OS exists
    os_exists = db.query(OS).filter(OS.id == device_data.os_id).first()
    if not os_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OS not found"
        )
    
    try:
        # Create new device
        new_device = Device(
            device_name=device_data.device_name,
            brand=device_data.brand,
            model=device_data.model,
            os_id=device_data.os_id,
            android_ui=device_data.android_ui
        )
        db.add(new_device)
        db.flush()  # Get the device ID
        
        # Associate device with user
        user_device = UserDevice(
            user_id=current_user.id,
            device_id=new_device.id,
            is_active=True
        )
        db.add(user_device)
        
        # Create initial setup record
        setup = Setup(
            user_id=current_user.id,
            device_id=new_device.id,
            is_completed=False
        )
        db.add(setup)
        
        db.commit()
        
        return {
            "message": "Device registered successfully",
            "device_id": new_device.id,
            "user_device_id": user_device.id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.get("/os-types", response_model=List[Dict[str, Any]])
async def get_os_types(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all available OS types and versions"""
    
    os_list = db.query(OS).all()
    result = []
    
    for os in os_list:
        result.append({
            "id": os.id,
            "name": os.name,
            "version": os.version,
            "type": os.type.value if os.type else None
        })
    
    return result


@router.put("/devices/{device_id}/deactivate", response_model=Dict[str, Any])
async def deactivate_device(
    device_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deactivate a device"""
    
    # Check if device belongs to user
    user_device = db.query(UserDevice).filter(
        UserDevice.user_id == current_user.id,
        UserDevice.device_id == device_id
    ).first()
    
    if not user_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found or does not belong to user"
        )
    
    # Deactivate device
    user_device.is_active = False
    db.commit()
    
    return {
        "message": "Device deactivated successfully",
        "device_id": device_id
    }
