import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import create_document, get_documents
from schemas import FurnitureProduct

app = FastAPI(title="OD Nameštaj API", description="API za prodaju nameštaja po meri")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "OD Nameštaj backend je spreman"}

@app.get("/api/hello")
def hello():
    return {"message": "Pozdrav sa backend API-ja!"}

# Products endpoints
class ProductCreate(FurnitureProduct):
    pass

@app.post("/api/products", response_model=dict)
def create_product(product: ProductCreate):
    try:
        inserted_id = create_document("furnitureproduct", product)
        return {"id": inserted_id, "status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products", response_model=List[dict])
def list_products(
    kategorija: Optional[str] = Query(None, description="Filter po kategoriji"),
    istaknuto: Optional[bool] = Query(None, description="Samo istaknuti proizvodi"),
    limit: Optional[int] = Query(50, ge=1, le=200, description="Maksimalan broj rezultata")
):
    try:
        filter_dict = {}
        if kategorija:
            filter_dict["kategorija"] = kategorija
        if istaknuto is not None:
            filter_dict["istaknuto"] = istaknuto
        docs = get_documents("furnitureproduct", filter_dict, limit)
        # Convert ObjectId to str if present
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
