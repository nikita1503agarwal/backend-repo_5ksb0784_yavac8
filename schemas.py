"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Custom schema for the furniture shop (Serbian fields)
class FurnitureProduct(BaseModel):
    """
    Kolekcija: "furnitureproduct"
    Schema za proizvode nameštaja po meri
    """
    naziv: str = Field(..., description="Naziv proizvoda")
    opis: Optional[str] = Field(None, description="Opis proizvoda")
    cena: float = Field(..., ge=0, description="Cena u EUR")
    kategorija: str = Field(..., description="Kategorija (npr. kuhinja, ormar, komoda)")
    dimenzije: Optional[str] = Field(None, description="Dimenzije (npr. 200x60x40 cm)")
    materijal: Optional[str] = Field(None, description="Materijal (npr. puno drvo, medijapan)")
    slike: Optional[List[HttpUrl]] = Field(default_factory=list, description="URL slike proizvoda")
    istaknuto: bool = Field(False, description="Da li je proizvod istaknut")
    dostupno: bool = Field(True, description="Dostupnost proizvoda")
