from sqlalchemy import create_engine, Column, BigInteger, String, Boolean, Date, Text, ForeignKey, Integer
from sqlalchemy.orm import declarative_base, relationship

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
    books = relationship("Book", back_populates="parent_list")
    docs = relationship("Doc", back_populates="parent_list")
    archives = relationship("Archives", back_populates="parent_list")
    articles = relationship("Article", back_populates="parent_list")
    interviews = relationship("Interview", back_populates="parent_list")


class Book(Base):
    __tablename__ = 'Books'

    book_id = Column(BigInteger, primary_key=True, autoincrement=True)
    is_ebook = Column(Boolean)
    book_title = Column(String(50), nullable=False)
    authors1_name = Column(String(50), nullable=False)
    authors1_surname = Column(String(50), nullable=False)
    authors2_name = Column(String(50))
    authors2_surname = Column(String(50))
    publisher_name = Column(String(50), nullable=False)
    publisher_city = Column(String(50), nullable=False)
    publisher_year = Column(String(50), nullable=False)
    refs = Column(String(50))
    link = Column(Text)
    notes = Column(String(50))
    date_of_pub = Column(Date)
    list_id = Column(BigInteger, ForeignKey('Lists.list_id'))

    parent_list = relationship("List", back_populates="books")


class Doc(Base):
    __tablename__ = 'Docs'

    doc_id = Column(BigInteger, primary_key=True, autoincrement=True)
    doc_title = Column(String(50), nullable=False)
    publisher_name = Column(String(50), nullable=False)
    publisher_city = Column(String(50), nullable=False)
    publisher_year = Column(String(50), nullable=False)
    refs = Column(String(50))
    list_id = Column(BigInteger, ForeignKey('Lists.list_id'))

    parent_list = relationship("List", back_populates="docs")


class Archives(Base):
    __tablename__ = 'Archives'

    arch_id = Column(BigInteger, primary_key=True, autoincrement=True)
    arch_title = Column(String(50), nullable=False)
    arch_location = Column(Text, nullable=False)
    refs = Column(String(50), nullable=False)
    list_id = Column(BigInteger, ForeignKey('Lists.list_id'))

    parent_list = relationship("List", back_populates="archives")


class Article(Base):
    __tablename__ = 'Articles'

    article_id = Column(BigInteger, primary_key=True, autoincrement=True)
    article_type = Column(String(50), nullable=False)
    article_title = Column(String(50), nullable=False)
    article_author = Column(String(50), nullable=False)
    article_link = Column(Text)
    magazine_title = Column(String(50))
    article_page = Column(Integer)
    list_id = Column(BigInteger, ForeignKey('Lists.list_id'))

    parent_list = relationship("List", back_populates="articles")


class Interview(Base):
    __tablename__ = 'Interviews'

    interview_id = Column(BigInteger, primary_key=True, autoincrement=True)
    getting_interviewed = Column(String(50), nullable=False)
    gi_year_of_birth = Column(Date, nullable=False)
    interviewing = Column(String(50), nullable=False)
    location_of_interview = Column(Text, nullable=False)
    interview_date = Column(Date, nullable=False)
    list_id = Column(BigInteger, ForeignKey('Lists.list_id'))

    parent_list = relationship("List", back_populates="interviews")
