import sqlalchemy
from sqlalchemy.util.preloaded import orm
from .db_session import SqlAlchemyBase


class Article(SqlAlchemyBase):
    __tablename__ = 'article'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name_event = sqlalchemy.Column(sqlalchemy.Text)
    co_authors = sqlalchemy.Column(sqlalchemy.Text)
    diploma = sqlalchemy.Column(sqlalchemy.Text)
    notes = sqlalchemy.Column(sqlalchemy.Text)
    approved = sqlalchemy.Column(sqlalchemy.Integer)
    id_person = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("people.id"))

    people = orm.relationship("People")