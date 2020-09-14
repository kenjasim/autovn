from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()
Session = scoped_session(sessionmaker()) 
# Create sql engine 
engine = create_engine('sqlite:///data.db', echo=False)

def bind_engine(engine):
    Base.metadata.bind = engine
    Session.configure(bind=engine)

def create_tables():
    Base.metadata.create_all(engine) 

def close_database():
    engine.dispose()

bind_engine(engine) 
        
# https://stackoverflow.com/questions/51106264/how-do-i-split-an-sqlalchemy-declarative-model-into-modules