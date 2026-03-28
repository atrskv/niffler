from datetime import date, datetime
from pydantic import BaseModel
from sqlmodel import SQLModel, Field
from faker import Faker

from internal.data.models.currency import Currency

fake = Faker()


class Category(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    username: str
    name: str


class Spend(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    amount: float
    description: str
    category_id: str = Field(foreign_key="category.id")
    spend_date: str
    currency: str
    username: str


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


class SpendAddUI(BaseModel):
    amount: str
    currency: Currency
    category: str
    input_date: date
    description: str

    @classmethod
    def random(cls) -> "SpendAddUI":
        random_date = fake.date_between(
            start_date=date(2000, 1, 1),
            end_date=date.today(),
        )

        return cls(
            amount=str(fake.random_int(min=10, max=100)),
            currency=fake.random_element(list(Currency)),
            category=fake.word(),
            input_date=random_date,
            description=fake.sentence(),
        )
