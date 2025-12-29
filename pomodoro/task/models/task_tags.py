"""Association table for tasks and tags."""

from sqlalchemy import Column, ForeignKey, Table

from pomodoro.database.database import Base

task_tag_table = Table(
    "task_tag",
    Base.metadata,
    Column(
        "task_id",
        ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
