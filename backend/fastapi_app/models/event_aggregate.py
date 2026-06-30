import uuid
from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from fastapi_app.database import Base

class EventAggregate(Base):
    """A daily rollup of raw events by type, per project.

    Raw events live in MongoDB; this table stores the aggregated counts
    (one row per project / event_type / event_date) that power analytics
    queries without scanning the raw event store.
    """

    __tablename__ = "event_aggregates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String, nullable=False, index=True)
    event_date = Column(Date, nullable=False, index=True)
    count = Column(Integer, default=0, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="aggregates")