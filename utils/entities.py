from pydantic import BaseModel, Field
from typing import Generic, List, Optional, TypeVar

T = TypeVar('T')  #  TypeVar("T")

class DataPage(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

class ItemCreate(BaseModel):
    name: str= Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=100)
    price: float = Field(..., ge=0)

class ItemPatch(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=100)
    price: Optional[float] = Field(None, ge=0)

class ItemOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    price: float
    created_utc: str
    updated_utc: str    