from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal

# Pydantic models map to Mongo collections by lowercased class name

class User(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    role: Literal["admin", "manager", "driver"] = "manager"
    avatar_url: Optional[str] = None
    bank_account: Optional[str] = None
    bank_ifsc: Optional[str] = None
    emergency_numbers: Optional[List[str]] = None

class Vehicle(BaseModel):
    plate: str = Field(..., description="Registration number")
    type: Literal["truck", "trailer", "container", "tanker", "van"] = "truck"
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    engine_on: bool = False
    gps_active: bool = True
    fuel_level: Optional[float] = None
    speed: Optional[float] = None
    status: Literal["idle", "enroute", "loaded", "unloaded", "maintenance"] = "idle"
    location: Optional[dict] = None  # {lat, lng}
    wallet_balance: float = 0.0

class Load(BaseModel):
    vehicle_id: Optional[str] = None
    product_name: str
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    amount: float
    loading_address: str
    unloading_address: str
    distance_km: Optional[float] = None
    rating: Optional[float] = None
    status: Literal["open", "accepted", "assigned", "in_transit", "delivered", "cancelled"] = "open"
    vehicle_type: Optional[Vehicle.__annotations__["type"]] = None

class WalletTransaction(BaseModel):
    user_id: Optional[str] = None
    vehicle_id: Optional[str] = None
    amount: float
    type: Literal["credit", "debit"]
    reason: Literal["recharge", "load_payment", "fuel", "refund", "other"] = "other"

class Document(BaseModel):
    vehicle_id: Optional[str] = None
    user_id: Optional[str] = None
    name: str
    content_type: str
    url: Optional[str] = None

class Notification(BaseModel):
    user_id: Optional[str] = None
    title: str
    body: str
    type: Literal[
        "vehicle_verification",
        "document_uploaded",
        "vehicle_approved",
        "fuel_theft",
        "vehicle_loaded",
        "vehicle_unloaded",
        "wallet_debited",
        "wallet_created",
        "load_confirmed",
    ] = "load_confirmed"
    read: bool = False
