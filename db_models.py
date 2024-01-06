from sqlalchemy import create_engine, Column, BigInteger, String, ForeignKey, Date
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'Users'

    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    chat_id = Column(BigInteger)

    lists = relationship("List", back_populates="owner")


class List(Base):
    __tablename__ = 'Lists'

    list_id = Column(BigInteger, primary_key=True, autoincrement=True)
    list_name = Column(String(50))
    list_owner = Column(BigInteger, ForeignKey('Users.user_id'))

    owner = relationship("User", back_populates="lists")
    entries = relationship("Entry", back_populates="parent_list")


class Entry(Base):
    __tablename__ = 'Entries'

    entry_id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(50))
    authors_name = Column(String(50))
    authors_surname = Column(String(50))
    year_of_publishing = Column(Date)
    publisher = Column(String(50))
    list_id = Column(BigInteger, ForeignKey('Lists.list_id'))

    parent_list = relationship("List", back_populates="entries")