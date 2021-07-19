from db import base
from sqlalchemy import *

class Assignment(base):
    __tablename__ = 'assignment'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    #datetime = Column(String)