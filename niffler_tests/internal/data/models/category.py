from uuid import uuid4
from faker import Faker
from pydantic import BaseModel

fake = Faker()


class CategoryAPI(BaseModel):
    id: str
    name: str
    username: str
    archived: bool = False

    @classmethod
    def random(cls, username: str) -> "CategoryAPI":
        return cls(
            id=str(uuid4()),
            name=fake.word().capitalize(),
            username=username,
            archived=False,
        )
