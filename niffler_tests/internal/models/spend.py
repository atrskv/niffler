from datetime import datetime
from pydantic import BaseModel
from sqlmodel import SQLModel, Field


class Category(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    username: str
    name: str


class Spend(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    amount: float
    description: str
    category_id: str = Field(foreign_key="category.id")
    spendDate: datetime
    currency: str


class CategoryAPI(BaseModel):
    id: str
    name: str
    username: str
    archived: bool = False


class SpendAPI(BaseModel):
    id: str
    amount: float
    description: str
    category: CategoryAPI
    spendDate: datetime
    currency: str


class SpendAddAPI(BaseModel):
    amount: float
    description: str
    category: str | None = None
    spendDate: str | None = None
    currency: str
