"""Birth chart service."""

from typing import Any

from sqlalchemy.orm import Session

from divyadrishti.astrology.generator import BirthChartGenerator
from divyadrishti.models import BirthChart
from divyadrishti.services.birth_profile_service import BirthProfileService


class BirthChartService:
    """Business logic for generated birth charts."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def store_chart(self, profile_id: int, chart_type: str, chart_data: dict[str, Any]) -> BirthChart:
        chart = BirthChart(profile_id=profile_id, chart_type=chart_type, chart_data=chart_data)
        self.db.add(chart)
        self.db.commit()
        self.db.refresh(chart)
        return chart

    def get_by_id(self, chart_id: int, user_id: int) -> BirthChart | None:
        return (
            self.db.query(BirthChart)
            .join(BirthChart.profile)
            .filter(BirthChart.id == chart_id, BirthChart.profile.has(user_id=user_id))
            .first()
        )

    def get_latest_chart(self, profile_id: int, chart_type: str | None = None) -> BirthChart | None:
        query = self.db.query(BirthChart).filter(BirthChart.profile_id == profile_id)
        if chart_type:
            query = query.filter(BirthChart.chart_type == chart_type)
        return query.order_by(BirthChart.generated_at.desc()).first()

    def list_by_profile(self, profile_id: int) -> list[BirthChart]:
        return (
            self.db.query(BirthChart)
            .filter(BirthChart.profile_id == profile_id)
            .order_by(BirthChart.generated_at.desc())
            .all()
        )

    def generate_chart(
        self,
        profile_id: int,
        user_id: int,
        chart_type: str = "rashi",
        store: bool = True,
    ) -> BirthChart:
        """Generate a birth chart for the given profile and optionally store it."""
        profile_service = BirthProfileService(self.db)
        profile = profile_service.get(profile_id, user_id)
        if not profile:
            raise ValueError("Profile not found")

        if profile.latitude is None or profile.longitude is None or not profile.timezone:
            raise ValueError(
                "Birth profile is missing latitude, longitude or timezone; "
                "please update the birth place or coordinates."
            )

        generator = BirthChartGenerator()
        chart_data = generator.generate(
            date_of_birth=profile.date_of_birth,
            time_of_birth=profile.time_of_birth,
            latitude=profile.latitude,
            longitude=profile.longitude,
            timezone=profile.timezone,
            chart_type=chart_type,
        )

        if chart_type == "rashi" and store:
            # Generate and store D9 alongside the D1 chart.
            varga = generator.generate_varga(
                date_of_birth=profile.date_of_birth,
                time_of_birth=profile.time_of_birth,
                latitude=profile.latitude,
                longitude=profile.longitude,
                timezone=profile.timezone,
                chart_type="navamsa",
            )
            self.store_chart(profile_id, "navamsa", varga.model_dump())

        if store:
            return self.store_chart(profile_id, chart_type, chart_data.model_dump())
        return BirthChart(
            profile_id=profile_id,
            chart_type=chart_type,
            chart_data=chart_data.model_dump(),
        )
