from ninja import Router

from users.auth import JWTAuth, roles_allowed
from ..models import Device
from ..schemas import DeviceCreateSchema, DeviceOutSchema, DeviceOutSchemaMydevice
from telemerty.models import DeviceTelemetry

router = Router(auth=JWTAuth())

print(f'Device router initialized with JWTAuth: {router.auth.__class__.__name__}')

@router.post("/creat", response=DeviceOutSchema)
@roles_allowed("admin", "user")
def create_device(request, payload: DeviceCreateSchema):
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return {"error": "Missing or invalid Authorization header"}
    
    token = auth_header.replace('Bearer ', '')
    auth = JWTAuth()
    user = auth.authenticate(request, token)
    print(f'Authenticated user: {user}')
    if not user:
        return {"error": "Invalid or expired token"}
    device = Device.objects.create(
        name=payload.name,
        type=payload.type,
        location=payload.location,
        owner=user
        
    )
    # Add device to user's device_ids
    user.device_ids.add(device)
    
    DeviceTelemetry.objects.create(device=device)
    device.save()
    return device

@router.get("/all/", response=list[DeviceOutSchema])
@roles_allowed("admin")
def list_devices(request):
    return Device.objects.all()

@router.get("/my-devices/", response=list[DeviceOutSchemaMydevice])
@roles_allowed("admin", "user")
def get_my_devices(request):
    user = request.auth
    devices = user.device_ids.all()
    
    # Update each device's state to the latest telemetry
    for device in devices:
        latest_telemetry = device.telemetry.first()  # first() gets the latest due to ordering
        if latest_telemetry:
            device.state = latest_telemetry
    
    return devices

@router.get("/{device_id}/", response=DeviceOutSchemaMydevice)
@roles_allowed("admin", "user")
def get_device(request, device_id: str):
    try:
        return Device.objects.get(device_id=device_id)
    except Device.DoesNotExist:
        return {"error": "Device not found"}


@router.delete("/{device_id}/")
@roles_allowed("admin", "user")
def delete_device(request, device_id: str):
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return {"error": "Missing or invalid Authorization header"}
    
    token = auth_header.replace('Bearer ', '')
    auth = JWTAuth()
    user = auth.authenticate(request, token)
    print(f'Authenticated user: {user}')
    if not user:
        return {"error": "Invalid or expired token"}
    
    try:
        device = Device.objects.filter(id=device_id).first()  # type: ignore
        if not device:
            return {"error": "Device not found"}
        device.delete()
        return {"message": "Device deleted successfully"}
    except Device.DoesNotExist:
        return {"error": "Device not found"}