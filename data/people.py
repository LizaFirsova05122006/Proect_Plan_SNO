import sqlalchemy
from sqlalchemy.util.preloaded import orm
from .db_session import SqlAlchemyBase


class People(SqlAlchemyBase):
    __tablename__ = 'people'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    surname = sqlalchemy.Column(sqlalchemy.Text)
    name = sqlalchemy.Column(sqlalchemy.Text)
    s_name = sqlalchemy.Column(sqlalchemy.Text)
    group = sqlalchemy.Column(sqlalchemy.Text)
    email = sqlalchemy.Column(sqlalchemy.Text)
    password = sqlalchemy.Column(sqlalchemy.Text)
    date_birth = sqlalchemy.Column(sqlalchemy.Text)
    id_role = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("roles.id"))

    roles = orm.relationship("Roles")
    contest = orm.relationship("Contest", back_populates='people')
    olimped = orm.relationship("Olimped", back_populates='people')
    award = orm.relationship("Award", back_populates='people')
    project = orm.relationship("Project", back_populates='people')
    scholarship = orm.relationship("Scholarship", back_populates='people')
    champioship = orm.relationship("Champioship", back_populates='people')