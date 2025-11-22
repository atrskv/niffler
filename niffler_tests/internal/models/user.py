from faker import Faker
from pydantic import BaseModel

fake = Faker()


class User(BaseModel):
    login: str
    password: str

    @classmethod
    def create_random(cls):
        password = fake.password()
        return cls(
            login=fake.pystr(min_chars=5, max_chars=12), password=password
        )
