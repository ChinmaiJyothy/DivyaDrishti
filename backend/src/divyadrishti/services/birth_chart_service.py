"""Birth chart service."""

from sqlalchemy.orm import Session

from divyadrishti.models import BirthChart


class BirthChartService:
    """Business logic for generated birth charts."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def store_chart(self, profile_id: int, chart_type: str, chart_data: dict) -> BirthChart:
        chart = BirthChart(profile_id=profile_id, chart_type=chart_type, chart_data=chart_data)
        self.db.add(chart)
        self.db.commit()
        self.db.refresh(chart)
        return chart

    def get_latest_chart(self, profile_id: int) -> BirthChart | None:
        return (
            self.db.query(BirthChart)
            .filter(BirthChart.profile_id == profile_id)
            .order_by(BirthChart.generated_at.desc())
            .first()
        )

    def list_by_profile(self, profile_id: int) -> list[BirthChart]:
        return (
            self.db.query(BirthChart)
            .filter(BirthChart.profile_id == profile_id)
            .order_by(BirthChart.generated_at.desc())
            .all()
        )
