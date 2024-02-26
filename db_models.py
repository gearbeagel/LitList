from sqlalchemy import Column, String, Integer, BigInteger, Boolean, Date, Text, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import relationship, declarative_base

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

    entries = relationship('Entry', back_populates='list')
    owner = relationship("User", back_populates="lists")
    books = relationship("Book", back_populates="parent_list")
    docs = relationship("Doc", back_populates="parent_list")
    archives = relationship("Archive", back_populates="parent_list")
    articles = relationship("Article", back_populates="parent_list")
    interviews = relationship("Interview", back_populates="parent_list")


class Entry(Base):
    __tablename__ = 'Entries'

    entry_id = Column(BigInteger, primary_key=True, autoincrement=True)
    from_book_resource_id = Column(BigInteger, ForeignKey('Books.book_id', ondelete='CASCADE'))
    from_doc_resource_id = Column(BigInteger, ForeignKey('Docs.doc_id', ondelete='CASCADE'))
    from_arch_resource_id = Column(BigInteger, ForeignKey('Archives.arch_id', ondelete='CASCADE'))
    from_artcl_resource_id = Column(BigInteger, ForeignKey('Articles.article_id', ondelete='CASCADE'))
    from_inter_resource_id = Column(BigInteger, ForeignKey('Interviews.interview_id', ondelete='CASCADE'))
    notes = Column(String(50))
    entry_type = Column(String(50))
    mentioning = Column(String(50))
    list_id = Column(BigInteger, ForeignKey('Lists.list_id'))

    book = relationship('Book', back_populates='entry')
    doc = relationship('Doc', back_populates='entry')
    archive = relationship('Archive', back_populates='entry')
    article = relationship('Article', back_populates='entry')
    interview = relationship('Interview', back_populates='entry')
    list = relationship('List', back_populates='entries')


class Book(Base):
    __tablename__ = 'Books'

    book_id = Column(BigInteger, primary_key=True, autoincrement=True)
    is_ebook = Column(Boolean)
    book_title = Column(String(50), nullable=False)
    authors1_name = Column(String(50), nullable=False)
    authors1_surname = Column(String(50), nullable=False)
    authors2_name = Column(String(50), nullable=False)
    authors2_surname = Column(String(50), nullable=False)
    publisher_name = Column(String(50), nullable=False)
    publisher_city = Column(String(50), nullable=False)
    publisher_year = Column(String(50), nullable=False)
    refs = Column(String(50))
    link = Column(Text)
    notes = Column(String(50))
    date_of_pub = Column(Date)
    list_id = Column(BigInteger, ForeignKey('Lists.list_id'))

    entry = relationship('Entry', back_populates='book')
    parent_list = relationship("List", back_populates="books")


class Doc(Base):
    __tablename__ = 'Docs'

    doc_id = Column(BigInteger, primary_key=True, autoincrement=True)
    doc_title = Column(String(50), nullable=False)
    doc_source = Column(String(50), nullable=False)
    doc_author_name = Column(String(50), nullable=False)
    doc_author_surname = Column(String(50), nullable=False)
    publisher_name = Column(String(50), nullable=False)
    publisher_city = Column(String(50), nullable=False)
    publisher_year = Column(Date, nullable=False)
    refs = Column(String(50))
    list_id = Column(BigInteger, ForeignKey('Lists.list_id'))

    entry = relationship('Entry', back_populates='doc')
    parent_list = relationship("List", back_populates="docs")


class Archive(Base):
    __tablename__ = 'Archives'

    arch_id = Column(BigInteger, primary_key=True, autoincrement=True)
    arch_title = Column(Text, nullable=False)
    arch_period = Column(String(50), nullable=False)
    arch_location = Column(Text, nullable=False)
    arch_placement = Column(Text, nullable=False)
    list_id = Column(BigInteger, ForeignKey('Lists.list_id'))

    entry = relationship('Entry', back_populates='archive')
    parent_list = relationship("List", back_populates="archives")


class Article(Base):
    __tablename__ = 'Articles'

    article_id = Column(BigInteger, primary_key=True, autoincrement=True)
    article_type = Column(String(50), nullable=False)
    article_title = Column(String(50), nullable=False)
    article_author_name = Column(String(50), nullable=False)
    article_author_surname = Column(String(50), nullable=False)
    article_link = Column(Text)
    article_dop = Column(Date)
    magazine_info = Column(String(50))
    source_title = Column(String(50))
    article_page = Column(Integer)
    access_date = Column(Date)
    list_id = Column(BigInteger, ForeignKey('Lists.list_id'))

    entry = relationship('Entry', back_populates='article')
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

    entry = relationship('Entry', back_populates='interview')
    parent_list = relationship("List", back_populates="interviews")
