from typing import Sequence

from sqlalchemy import create_engine, Engine, delete
from sqlmodel import Session, select

from internal.data.models.spend import Category, Spend
from sqlalchemy import event
from allure_commons.types import AttachmentType
import allure


class SpendDb:
    engine: Engine

    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)

        event.listen(self.engine, "do_execute", fn=self.attach_sql)

    @staticmethod
    def attach_sql(cursor, statement, parameters, context):
        statement_with_params = statement % parameters
        name = statement.split(" ")[0] + " " + context.engine.url.database
        allure.attach(
            statement_with_params, name=name, attachment_type=AttachmentType.TEXT
        )

    def get_user_categories(self, username: str) -> Sequence[Category]:
        with Session(self.engine) as session:
            statement = select(Category).where(Category.username == username)
            return session.exec(statement).all()

    def delete_spends_by_category_id(self, category_id: str) -> None:
        with Session(self.engine) as session:
            stmt = delete(Spend).where(Spend.category_id == category_id)
            session.execute(stmt)
            session.commit()

    def delete_category_by_id(self, category_id: str) -> None:
        with Session(self.engine) as session:
            category = session.get(Category, category_id)
            if category:
                session.delete(category)
                session.commit()

    def get_spends_by_username(self, username: str) -> Sequence[Spend]:
        with Session(self.engine) as session:
            statement = select(Spend).where(Spend.username == username)
            return session.exec(statement).all()
