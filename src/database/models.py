"""
Database models and schema for the Federal Budget Analysis project.

Uses SQLAlchemy ORM with SQLite backend.
"""

from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, Float, String, Date, DateTime,
    Text, UniqueConstraint, Index
)
from sqlalchemy.orm import declarative_base, sessionmaker
from loguru import logger

from src.utils.config import load_config, PROJECT_ROOT

Base = declarative_base()


class EconomicSeries(Base):
    """Metadata about each economic data series."""
    __tablename__ = "economic_series"

    id = Column(Integer, primary_key=True, autoincrement=True)
    series_id = Column(String(50), unique=True, nullable=False, index=True)
    source = Column(String(20), nullable=False)  # FRED, BEA, Census, Treasury, CBO
    title = Column(String(255))
    units = Column(String(100))
    frequency = Column(String(20))  # Daily, Monthly, Quarterly, Annual
    seasonal_adjustment = Column(String(50))
    last_updated = Column(DateTime)
    notes = Column(Text)

    def __repr__(self):
        return f"<EconomicSeries(series_id='{self.series_id}', source='{self.source}')>"


class Observation(Base):
    """Individual data observations (time series values)."""
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    series_id = Column(String(50), nullable=False, index=True)
    date = Column(Date, nullable=False)
    value = Column(Float)
    realtime_start = Column(Date)
    realtime_end = Column(Date)

    __table_args__ = (
        UniqueConstraint("series_id", "date", name="uq_series_date"),
        Index("ix_series_date", "series_id", "date"),
    )

    def __repr__(self):
        return f"<Observation(series_id='{self.series_id}', date='{self.date}', value={self.value})>"


class PolicyEvent(Base):
    """Significant policy events for event-study analysis."""
    __tablename__ = "policy_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    category = Column(String(50))  # tax, tariff, spending, monetary
    date_enacted = Column(Date, nullable=False)
    date_effective = Column(Date)
    description = Column(Text)
    source_url = Column(String(500))

    def __repr__(self):
        return f"<PolicyEvent(name='{self.name}', date='{self.date_enacted}')>"


class TariffSchedule(Base):
    """Tariff rates by product/country for trade analysis."""
    __tablename__ = "tariff_schedule"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hts_code = Column(String(20))  # Harmonized Tariff Schedule code
    description = Column(String(500))
    country = Column(String(100))
    rate_pct = Column(Float)  # Ad valorem tariff rate
    effective_date = Column(Date, nullable=False)
    end_date = Column(Date)
    authority = Column(String(100))  # Section 201, 232, 301, etc.
    notes = Column(Text)

    __table_args__ = (
        Index("ix_tariff_country_date", "country", "effective_date"),
    )

    def __repr__(self):
        return f"<TariffSchedule(hts='{self.hts_code}', country='{self.country}', rate={self.rate_pct}%)>"


class CollectionLog(Base):
    """Log of data collection runs for auditability."""
    __tablename__ = "collection_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(20), nullable=False)
    series_id = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)
    records_fetched = Column(Integer, default=0)
    status = Column(String(20))  # success, error, partial
    error_message = Column(Text)

    def __repr__(self):
        return f"<CollectionLog(source='{self.source}', series='{self.series_id}', status='{self.status}')>"


# ---------------------------------------------------------------------------
# Engine & Session management
# ---------------------------------------------------------------------------

_engine = None
_Session = None


def get_engine(config: dict = None):
    """Create or return the SQLAlchemy engine."""
    global _engine
    if _engine is None:
        if config is None:
            config = load_config()
        db_url = config.get("database", {}).get("url", "sqlite:///data/federal_budget.db")
        # Make path relative to project root for SQLite
        if db_url.startswith("sqlite:///") and not db_url.startswith("sqlite:////"):
            db_path = PROJECT_ROOT / db_url.replace("sqlite:///", "")
            db_path.parent.mkdir(parents=True, exist_ok=True)
            db_url = f"sqlite:///{db_path}"
        echo = config.get("database", {}).get("echo", False)
        _engine = create_engine(db_url, echo=echo)
        logger.info(f"Database engine created: {db_url}")
    return _engine


def get_session(config: dict = None):
    """Create a new database session."""
    global _Session
    if _Session is None:
        engine = get_engine(config)
        _Session = sessionmaker(bind=engine)
    return _Session()


def init_database(config: dict = None):
    """Initialize the database — create all tables."""
    engine = get_engine(config)
    Base.metadata.create_all(engine)
    logger.info("Database tables created successfully.")
    return engine
