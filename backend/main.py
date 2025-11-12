from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from schemas import User, Vehicle, Load, WalletTransaction, Document, Notification
from database import db, create_document, get_documents, get_document, update_document, delete_document, save_document_file

app = FastAPI(title="Fleet Manager API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/test")
async def test():
    # Quick DB sanity check
    try:
        await db.command("ping")
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

# Users
@app.post("/users", response_model=dict)
async def create_user(user: User):
    _id = await create_document("user", user.model_dump())
    return {"id": _id}

@app.get("/users", response_model=List[dict])
async def list_users():
    return await get_documents("user", limit=200)

# Vehicles
@app.post("/vehicles", response_model=dict)
async def add_vehicle(vehicle: Vehicle):
    _id = await create_document("vehicle", vehicle.model_dump())
    return {"id": _id}

@app.get("/vehicles", response_model=List[dict])
async def list_vehicles(type: Optional[str] = None):
    filt = {"type": type} if type else {}
    return await get_documents("vehicle", filt, limit=500)

@app.patch("/vehicles/{vehicle_id}")
async def update_vehicle(vehicle_id: str, vehicle: Vehicle):
    updated = await update_document("vehicle", vehicle_id, vehicle.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"ok": True}

# Loads
@app.post("/loads", response_model=dict)
async def create_load(load: Load):
    _id = await create_document("load", load.model_dump())
    return {"id": _id}

@app.get("/loads", response_model=List[dict])
async def list_loads(status: Optional[str] = None):
    filt = {"status": status} if status else {}
    return await get_documents("load", filt, limit=500)

@app.post("/loads/{load_id}/accept")
async def accept_load(load_id: str, vehicle_id: str):
    load_doc = await get_document("load", load_id)
    if not load_doc:
        raise HTTPException(404, "Load not found")
    if load_doc.get("status") not in ["open", "accepted"]:
        raise HTTPException(400, "Load not available")
    await update_document("load", load_id, {"status": "accepted", "vehicle_id": vehicle_id})
    return {"ok": True}

# Wallet
@app.post("/wallet/transactions", response_model=dict)
async def wallet_tx(tx: WalletTransaction):
    _id = await create_document("wallettransaction", tx.model_dump())
    if tx.vehicle_id and tx.type == "credit":
        # naive balance update
        veh = await get_documents("vehicle", {"_id": {"$exists": True}, "_id": {"$exists": True}}, limit=0)
    return {"id": _id}

@app.get("/wallet/transactions", response_model=List[dict])
async def list_wallet_tx(vehicle_id: Optional[str] = None, user_id: Optional[str] = None):
    filt = {}
    if vehicle_id:
        filt["vehicle_id"] = vehicle_id
    if user_id:
        filt["user_id"] = user_id
    return await get_documents("wallettransaction", filt, limit=500, sort=[("created_at", -1)])

# Documents upload (DMS)
@app.post("/documents/upload", response_model=dict)
async def upload_document(name: str, content_type: str, vehicle_id: Optional[str] = None, user_id: Optional[str] = None, file: UploadFile = File(...)):
    data = {"name": name, "content_type": content_type, "vehicle_id": vehicle_id, "user_id": user_id}
    content = await file.read()
    doc_id = await save_document_file(data, content)
    return {"id": doc_id}

@app.get("/notifications", response_model=List[dict])
async def list_notifications(user_id: Optional[str] = None, unread_only: bool = False):
    filt = {"user_id": user_id} if user_id else {}
    if unread_only:
        filt["read"] = False
    return await get_documents("notification", filt, limit=200, sort=[("created_at", -1)])

@app.post("/notifications", response_model=dict)
async def create_notification(n: Notification):
    _id = await create_document("notification", n.model_dump())
    return {"id": _id}
