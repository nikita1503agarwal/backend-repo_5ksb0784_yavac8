import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

from database import create_document, get_documents, create_documents
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


class ImportRequest(BaseModel):
    url: str

@app.post("/api/products/import", response_model=dict)
def import_products(req: ImportRequest):
    """Uvozi proizvode sa zadatog URL-a (očekuje JSON listu objekata). Pokušava mapiranje polja."""
    try:
        r = requests.get(req.url, timeout=15)
        if r.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Ne mogu da preuzmem podatke: {r.status_code}")
        data = r.json()
        if not isinstance(data, list):
            raise HTTPException(status_code=400, detail="Očekivana je lista proizvoda u JSON formatu")

        mapped = []
        for item in data:
            # Pokušaj mapiranja raznih mogućih ključeva na našu šemu
            naziv = item.get('naziv') or item.get('title') or item.get('name') or 'Proizvod'
            opis = item.get('opis') or item.get('description')
            cena = item.get('cena') or item.get('price') or 0
            try:
                cena = float(cena)
            except Exception:
                cena = 0.0
            kategorija = (item.get('kategorija') or item.get('category') or 'ostalo').lower()
            dimenzije = item.get('dimenzije') or item.get('dimensions')
            materijal = item.get('materijal') or item.get('material')
            slike = item.get('slike') or item.get('images') or []
            if isinstance(slike, str):
                slike = [slike]
            istaknuto = bool(item.get('istaknuto') or item.get('featured') or False)
            dostupno = bool(item.get('dostupno') if 'dostupno' in item else item.get('available', True))

            mapped.append({
                'naziv': naziv,
                'opis': opis,
                'cena': cena,
                'kategorija': kategorija,
                'dimenzije': dimenzije,
                'materijal': materijal,
                'slike': slike,
                'istaknuto': istaknuto,
                'dostupno': dostupno,
            })

        if not mapped:
            return {"inserted": 0, "status": "no-data"}

        ids = create_documents("furnitureproduct", mapped)
        return {"inserted": len(ids), "status": "ok"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/products/import/demo", response_model=dict)
def import_demo_products():
    """Seed/demo import kada nema JSON izvora. Ubacuje nekoliko primer proizvoda."""
    try:
        demo = [
            {
                'naziv': 'Kuhinjski Element "Dunav"',
                'opis': 'Moderna kuhinjska donja komoda sa tiho-zatvarajućim šarkama.',
                'cena': 420.0,
                'kategorija': 'kuhinja',
                'dimenzije': '80x60x90 cm',
                'materijal': 'MDF, bukva',
                'slike': [
                    'https://images.unsplash.com/photo-1556909212-d5b604d0c46e',
                    'https://images.unsplash.com/photo-1555041469-a586c61ea9bc'
                ],
                'istaknuto': True,
                'dostupno': True
            },
            {
                'naziv': 'Ormar "Avalski"',
                'opis': 'Ugradni ormar sa kliznim vratima i ogledalom.',
                'cena': 890.0,
                'kategorija': 'ormar',
                'dimenzije': '220x200x60 cm',
                'materijal': 'Iverica premium, aluminijum',
                'slike': ['https://images.unsplash.com/photo-1582582621959-48c79f2465f0'],
                'istaknuto': False,
                'dostupno': True
            },
            {
                'naziv': 'Komoda "Tisa"',
                'opis': 'Niska TV komoda sa tri fioke i otvorenim policama.',
                'cena': 310.0,
                'kategorija': 'komoda',
                'dimenzije': '160x45x45 cm',
                'materijal': 'Hrast masiv + furnir',
                'slike': ['https://images.unsplash.com/photo-1505692794403-34d4982f88aa'],
                'istaknuto': True,
                'dostupno': True
            },
            {
                'naziv': 'Radni sto "Morava"',
                'opis': 'Minimalistički radni sto sa skrivenim kanalom za kablove.',
                'cena': 260.0,
                'kategorija': 'radni sto',
                'dimenzije': '140x70x75 cm',
                'materijal': 'Jasen masiv',
                'slike': ['https://images.unsplash.com/photo-1493666438817-866a91353ca9'],
                'istaknuto': False,
                'dostupno': True
            }
        ]
        ids = create_documents("furnitureproduct", demo)
        return {"inserted": len(ids), "status": "ok", "demo": True}
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
