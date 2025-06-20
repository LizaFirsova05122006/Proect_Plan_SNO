import sqlalchemy
from sqlalchemy.util.preloaded import orm
from .db_session import SqlAlchemyBase


class Roles(SqlAlchemyBase):
    __tablename__ = 'roles'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    role = sqlalchemy.Column(sqlalchemy.Text, nullable=True)

    people = orm.relationship("People", back_populates='roles')