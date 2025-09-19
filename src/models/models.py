import pytz
from db import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Time, BigInteger, Date
from sqlalchemy import func


class Department(Base):
    __tablename__ = "department"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)


class Master(Base):
    __tablename__ = "master"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=True)
    tg_id = Column(BigInteger(), unique=True, nullable=False)
    is_manager = Column(Boolean(), default=False)
    department = Column(Integer(), ForeignKey("department.id"), nullable=True)
    is_blocked = Column(Boolean(), default=False)



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
    created_at = Column(DateTime(timezone=True), default=func.now())
    link = Column(String(300), nullable=False)
    category = Column(String(300), nullable=True)


class DayOff(Base):
    __tablename__ = "day_off"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    master = Column(Integer(), ForeignKey("master.id"))
    date = Column(Date(), nullable=False, default=func.current_date())


class DisciplineViolation(Base):
    __tablename__ = "discipline_violation"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    master = Column(Integer(), ForeignKey("master.id"))
    date = Column(Date(), nullable=False, default=func.current_date())


class GeneralCleaning(Base):
    __tablename__ = "general_cleaning"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    date = Column(Date(), nullable=False)


class GeneralCleaningReaction(Base):
    __tablename__ = "general_cleaning_reaction"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    master = Column(Integer(), ForeignKey("master.id"))
    general_cleaning = Column(Integer(), ForeignKey("general_cleaning.id"))
    is_confirmed = Column(Boolean(), default=False)
    text = Column(String(500), nullable=True)