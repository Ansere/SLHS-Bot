from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

sessionmaker = sessionmaker()
base = declarative_base()
session = sessionmaker()


def bind_engine(engine):
    global session
    base.metadata.bind = engine
    session = Session(sessionmaker.configure(bind=engine))
    base.metadata.create_all(engine)


"""
servermember_assignments = Table('member-assignment', Base.metadata,
   Column("servermember_id", Integer, ForeignKey("servermember.id")),
   Column("assignment_id", Integer, ForeignKey("assignment.id")),
)
"""
