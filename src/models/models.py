from db import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Time
from datetime import datetime


class Department(Base):
    __tablename__ = "department"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)


class Master(Base):
    __tablename__ = "master"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=True)
    tg_id = Column(Integer(), unique=True, nullable=False)
    is_manager = Column(Boolean(), default=False)
    department = Column(Integer(), ForeignKey("department.id"))


class Schedule(Base):
    __tablename__ = "schedule"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    master = Column(Integer(), ForeignKey("master.id"))
    time_start = Column(Time(), nullable=False)
    time_end = Column(Time(), nullable=False)


class Image(Base):
    __tablename__ = "image"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    master = Column(Integer(), ForeignKey("master.id"))
    created_at = Column(DateTime(), default=datetime.now)
    link = Column(String(300), nullable=False)