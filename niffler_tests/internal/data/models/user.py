import string
from uuid import uuid4
from faker import Faker
from pydantic import BaseModel

from internal.data.models.currency import Currency
from internal.data.models.fiends import FriendshipStatus
import random

fake = Faker()


class UserUI(BaseModel):
    login: str
    password: str

    @classmethod
    def random(cls):
        password = fake.password()
        return cls(login=fake.pystr(min_chars=5, max_chars=12), password=password)


class User(BaseModel):
    id: str
    username: str
    firstname: str | None = None
    password: str | None = None
    surname: str | None = None
    fullname: str | None = None
    currency: Currency | None = None
    photo: str | None = None
    photoSmall: str | None = None
    friendshipStatus: FriendshipStatus | None = None

    @classmethod
    def random(cls, username: str = "") -> "User":
        password_length = random.randint(5, 12)
        username_length = random.randint(5, 12)

        fake_username = "".join(
            random.choices(string.ascii_lowercase, k=username_length)
        )

        return cls(
            id=str(uuid4()),
            username=username or fake_username,
            firstname=fake.first_name(),
            password=fake.password(length=password_length),
            surname=fake.last_name(),
            fullname=fake.name(),
            currency=fake.random_element(list(Currency)),
            photo=None,
            photoSmall=None,
            friendshipStatus=None,
        )


class KafkaUserEvent(BaseModel):
    username: str
