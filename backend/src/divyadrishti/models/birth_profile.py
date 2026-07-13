"""Birth profile and chart models."""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy import orm
from sqlalchemy.orm import Mapped, mapped_column

from divyadrishti.database.database import Base


class BirthProfile(Base):
    """A birth profile owned by a user (self, spouse, child, etc.)."""

    __tablename__ = "birth_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    profile_name: Mapped[str] = mapped_column(String(255), nullable=False)
    relationship: Mapped[str] = mapped_column(String(50), nullable=False)
    date_of_birth: Mapped[str] = mapped_column(String(50), nullable=False)
    time_of_birth: Mapped[str] = mapped_column(String(50), nullable=True)
    birth_place: Mapped[str] = mapped_column(String(255), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    timezone: Mapped[str] = mapped_column(String(100), default="UTC")
    accuracy_level: Mapped[str] = mapped_column(String(50), default="exact")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    chart_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = orm.relationship("User", back_populates="birth_profiles")
    birth_charts: Mapped[list["BirthChart"]] = orm.relationship("BirthChart", back_populates="profile")
    conversations: Mapped[list["Conversation"]] = orm.relationship("Conversation", back_populates="birth_profile")


class BirthChart(Base):
    """A generated Vedic birth chart for a birth profile."""

    __tablename__ = "birth_charts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("birth_profiles.id"), nullable=False, index=True)
    chart_type: Mapped[str] = mapped_column(String(50), default="rashi")
    chart_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    profile: Mapped["BirthProfile"] = orm.relationship("BirthProfile", back_populates="birth_charts")
    planet_positions: Mapped[list["PlanetPosition"]] = orm.relationship("PlanetPosition", back_populates="birth_chart")
    house_positions: Mapped[list["HousePosition"]] = orm.relationship("HousePosition", back_populates="birth_chart")
    dashas: Mapped[list["Dasha"]] = orm.relationship("Dasha", back_populates="birth_chart")


class PlanetPosition(Base):
    """A planet's position in a birth chart."""

    __tablename__ = "planet_positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    birth_chart_id: Mapped[int] = mapped_column(ForeignKey("birth_charts.id"), nullable=False, index=True)
    planet: Mapped[str] = mapped_column(String(50), nullable=False)
    house: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sign: Mapped[str | None] = mapped_column(String(50), nullable=True)
    nakshatra: Mapped[str | None] = mapped_column(String(100), nullable=True)
    dignity: Mapped[str | None] = mapped_column(String(50), nullable=True)
    retrograde: Mapped[bool] = mapped_column(Boolean, default=False)
    combust: Mapped[bool] = mapped_column(Boolean, default=False)
    degree: Mapped[float | None] = mapped_column(Float, nullable=True)

    birth_chart: Mapped["BirthChart"] = orm.relationship("BirthChart", back_populates="planet_positions")


class HousePosition(Base):
    """A house and its lord/occupants in a birth chart."""

    __tablename__ = "house_positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    birth_chart_id: Mapped[int] = mapped_column(ForeignKey("birth_charts.id"), nullable=False, index=True)
    house: Mapped[int] = mapped_column(Integer, nullable=False)
    sign: Mapped[str | None] = mapped_column(String(50), nullable=True)
    lord: Mapped[str | None] = mapped_column(String(50), nullable=True)
    planets: Mapped[str | None] = mapped_column(Text, nullable=True)

    birth_chart: Mapped["BirthChart"] = orm.relationship("BirthChart", back_populates="house_positions")


class Dasha(Base):
    """A dasha period for a birth chart."""

    __tablename__ = "dashas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    birth_chart_id: Mapped[int] = mapped_column(ForeignKey("birth_charts.id"), nullable=False, index=True)
    planet: Mapped[str] = mapped_column(String(50), nullable=False)
    start_date: Mapped[str] = mapped_column(String(50), nullable=True)
    end_date: Mapped[str] = mapped_column(String(50), nullable=True)
    is_main: Mapped[bool] = mapped_column(Boolean, default=False)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)

    birth_chart: Mapped["BirthChart"] = orm.relationship("BirthChart", back_populates="dashas")
