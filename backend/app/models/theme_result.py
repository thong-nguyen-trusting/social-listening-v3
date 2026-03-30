from sqlalchemy import CheckConstraint, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ThemeResult(Base):
    __tablename__ = "theme_results"
    __table_args__ = (
        CheckConstraint(
            "label IN ('pain_point','positive_feedback','question','comparison','other')",
            name="ck_theme_results_label",
        ),
        CheckConstraint(
            "dominant_sentiment IN ('positive','negative','neutral')",
            name="ck_theme_results_dominant_sentiment",
        ),
    )

    theme_id: Mapped[str] = mapped_column(Text, primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("plan_runs.run_id"), nullable=False)
    label: Mapped[str] = mapped_column(Text, nullable=False)
    dominant_sentiment: Mapped[str] = mapped_column(Text, nullable=False)
    post_count: Mapped[int] = mapped_column(Integer, nullable=False)
    sample_quotes: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default="CURRENT_TIMESTAMP",
    )

