from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class Notification:
    id: str
    title: str
    body: str
    type: str
    grade: str
    section: str
    read: bool
    created_at: str


_store: list[Notification] = []


def create_timetable_notification(grade: str, section: str) -> Notification:
    notification = Notification(
        id=str(uuid4()),
        title="Timetable Updated",
        body=f"Your Grade {grade} • Section {section} timetable has been updated. Check your schedule for the latest periods.",
        type="timetable",
        grade=grade,
        section=section.upper(),
        read=False,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    _store.insert(0, notification)
    return notification


def list_notifications(grade: str | None = None, section: str | None = None) -> list[dict]:
    items = _store
    if grade and section:
        items = [item for item in _store if item.grade == grade and item.section == section.upper()]
    return [asdict(item) for item in items]


def mark_read(notification_id: str) -> bool:
    for item in _store:
        if item.id == notification_id:
            item.read = True
            return True
    return False
