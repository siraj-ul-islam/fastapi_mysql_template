import urllib
from sqlalchemy.ext.declarative import declarative_base
import sqlite3

from databases import Database
from environs import Env
from sqlalchemy import (
    Column,
    Integer,
    BIGINT,
    SmallInteger,
    Float,
    MetaData,
    String,
    Table,
    DateTime,
    Text,
    create_engine,
    Enum,
    ForeignKey,
)

env = Env()
env.read_env()
db = env("DATABASE")
user = env("USER_")
password = env("PASSWORD")
host = env("HOST")
dbname = env("DBNAME")
SQLALCHEMY_DATABASE_URL = "{0}://{1}:{2}@{3}/{4}".format(db, user, urllib.parse.quote_plus(password), host, dbname)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
metadata = MetaData()
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()
database = Database(SQLALCHEMY_DATABASE_URL)
# database = Database(SQLALCHEMY_DATABASE_URL, minsize=5, maxsize=500)

Notes = Table(
    "notes",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("title", String(255), unique=True),
    Column("content", String(255), nullable=True),
    Column("created_at", DateTime),
    Column("updated_at", DateTime)
)


Users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, unique=True),
    Column("name", String(191)),
    Column("email", String(191)),
    Column("profile_image", String(255), nullable=True),
    Column("email_verified_at", DateTime, nullable=True),
    Column("password", String(191)),
    Column("remember_token", String(100), nullable=True),
    Column("user_type", String(255), nullable=True),
    Column("credit", String(255), default='0', nullable=True),
    Column("created_at", DateTime),
    Column("updated_at", DateTime)
)
