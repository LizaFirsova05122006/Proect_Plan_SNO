import sqlalchemy
from sqlalchemy.util.preloaded import orm
from .db_session import SqlAlchemyBase


class FAQ(SqlAlchemyBase):
    __tablename__ = 'faq'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    question = sqlalchemy.Column(sqlalchemy.Text)
    answer = sqlalchemy.Column(sqlalchemy.Text)