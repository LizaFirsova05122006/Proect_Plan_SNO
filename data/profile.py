import sqlalchemy
from sqlalchemy.util.preloaded import orm
from .db_session import SqlAlchemyBase


class Profile(SqlAlchemyBase):
    __tablename__ = 'profile'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    email = sqlalchemy.Column(sqlalchemy.Text)
    photo = sqlalchemy.Column(sqlalchemy.Text)