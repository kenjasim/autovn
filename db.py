from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.engine.reflection import Inspector
from pathlib import Path 
import os 

# Create db path 
p = Path().parent.absolute() / "tmp"
if not os.path.isdir(str(p)): 
    os.mkdir(str(p)) 

Base = declarative_base()
Session = scoped_session(sessionmaker())
# Create sql engine
engine = create_engine('sqlite:///tmp/data.db', echo=False, connect_args={'check_same_thread': False})

def bind_engine(engine):
    """Bind the SQL Query engine to the database"""
    Base.metadata.bind = engine
    Session.configure(bind=engine)

def create_tables():
    """Initialise all tables in the database"""
    Base.metadata.create_all(engine)

def return_tables():
    """Return all tables in the database"""
    inspector = Inspector.from_engine(engine)
    return inspector.get_table_names() 

def close_database():
    """Close the database"""
    engine.dispose()

bind_engine(engine)

# https://stackoverflow.com/questions/51106264/how-do-i-split-an-sqlalchemy-declarative-model-into-modules
