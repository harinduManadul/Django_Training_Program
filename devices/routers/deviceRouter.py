from ninja import Router

from users.auth import JWTAuth, roles_allowed
from ..models import Device
from ..schemas import DeviceCreateSchema, DeviceOutSchema, DeviceOutSchemaMydevice, DeviceUpdateSchema, ErrorSchema
from telemerty.models import DeviceTelemetry

router = Router(auth=JWTAuth())

print(f'Device router initialized with JWTAuth: {router.auth.__class__.__name__}')

@router.post("/creat", response={
    200: DeviceOutSchema,
    401: ErrorSchema
})
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

@router.get("/all/", response={
    200: list[DeviceOutSchema],
    401: ErrorSchema
})
@roles_allowed("admin")
def list_devices(request):
    return Device.objects.all()

@router.get("/my-devices/", response={
    200: list[DeviceOutSchemaMydevice],
    401: ErrorSchema
})
@roles_allowed("admin", "user")
def get_my_devices(request):
    user = request.auth
    devices = user.device_ids.all()
    
    return devices

@router.get("/{device_id}/", response={
    200: DeviceOutSchema,
    404: ErrorSchema
})
@roles_allowed("admin", "user")
def get_device(request, device_id: str):
    try:
        device = Device.objects.get(device_id=device_id)
        # Get latest telemetry for the device
        latest_telemetry = DeviceTelemetry.objects.filter(device=device).order_by('-timestamp').first()
        device.telemetry = latest_telemetry
        return device
    except Device.DoesNotExist:
        return {"error": "Device not found"}


@router.put("/{device_id}/", response={
    200: DeviceOutSchema,
    404: ErrorSchema
})
@roles_allowed("admin", "user")
def update_device(request, device_id: str, payload: DeviceUpdateSchema):
    try:
        device = Device.objects.get(device_id=device_id, owner=request.auth)
    except Device.DoesNotExist:
        return {"error": "Device not found"}
    
    if payload.name is not None:
        device.name = payload.name
    if payload.type is not None:
        device.type = payload.type
    if payload.location is not None:
        device.location = payload.location
    if payload.is_active is not None:
        device.is_active = payload.is_active
    
    device.save()
    return device


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