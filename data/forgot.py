import sqlalchemy
from sqlalchemy.util.preloaded import orm
from .db_session import SqlAlchemyBase


class Forgot(SqlAlchemyBase):
    __tablename__ = 'forgot'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    email = sqlalchemy.Column(sqlalchemy.Text)
    code = sqlalchemy.Column(sqlalchemy.Text)
    used = sqlalchemy.Column(sqlalchemy.Integer)
