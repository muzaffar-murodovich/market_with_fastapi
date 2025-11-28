from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("postgresql://postgres:1234@localhost/delivery_db",
                       echo=True)
Base = declarative_base()
Session = sessionmaker()
