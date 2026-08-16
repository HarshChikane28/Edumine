from collections import defaultdict
from dataclasses import dataclass
from datetime import time
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Subject, TimetableSlot


DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri")
PERIODS = (
    (1, "09:00", time(9, 0), time(10, 0)),
    (2, "10:00", time(10, 0), time(11, 0)),
    (3, "11:30", time(11, 30), time(12, 30)),
    (4, "01:00", time(13, 0), time(14, 0)),
)
PERIOD_BY_TIME = {label: (number, starts, ends) for number, label, starts, ends in PERIODS}


@dataclass(frozen=True)
class RecommendationSlot:
    day_of_week: int
    period_number: int
    subject_id: UUID
    teacher_id: UUID


async def generate_recommendation(db: AsyncSession, class_id: UUID) -> tuple[list[RecommendationSlot], list[str]]:
    """Create a deterministic weekly schedule without modifying stored slots."""
    subjects = list((await db.scalars(select(Subject).where(Subject.class_id == class_id).order_by(Subject.name))).all())
    schedulable = [subject for subject in subjects if subject.teacher_id and subject.weekly_periods > 0]
    warnings = [f"{subject.name} has no assigned teacher or weekly workload." for subject in subjects if subject not in schedulable]
    requested_periods = sum(subject.weekly_periods for subject in schedulable)
    capacity = len(DAYS) * len(PERIODS)
    if requested_periods > capacity:
        warnings.append(f"Requested {requested_periods} periods but this class has only {capacity} weekly slots.")

    occupied_by_teacher = {
        (slot.teacher_id, slot.day_of_week, slot.period_number)
        for slot in (await db.scalars(select(TimetableSlot).where(TimetableSlot.class_id != class_id))).all()
    }
    class_occupied: set[tuple[int, int]] = set()
    teacher_daily_load: dict[tuple[UUID, int], int] = defaultdict(int)
    subject_daily_count: dict[tuple[UUID, int], int] = defaultdict(int)
    subject_periods: dict[UUID, list[tuple[int, int]]] = defaultdict(list)
    remaining = {subject.id: subject.weekly_periods for subject in schedulable}
    slots: list[RecommendationSlot] = []

    while any(count > 0 for count in remaining.values()):
        made_assignment = False
        for subject in sorted(schedulable, key=lambda item: (-remaining[item.id], item.name)):
            if remaining[subject.id] <= 0:
                continue
            candidates: list[tuple[tuple[int, int, int, int], int, int]] = []
            for day_index in range(len(DAYS)):
                for period_number, _, _, _ in PERIODS:
                    key = (day_index, period_number)
                    teacher_key = (subject.teacher_id, day_index, period_number)
                    if key in class_occupied or teacher_key in occupied_by_teacher:
                        continue
                    adjacent = sum(existing_day == day_index and abs(existing_period - period_number) == 1 for existing_day, existing_period in subject_periods[subject.id])
                    candidates.append(((subject_daily_count[(subject.id, day_index)], adjacent, teacher_daily_load[(subject.teacher_id, day_index)], period_number), day_index, period_number))
            if not candidates:
                continue
            _, day_index, period_number = min(candidates)
            slots.append(RecommendationSlot(day_index, period_number, subject.id, subject.teacher_id))
            class_occupied.add((day_index, period_number)); occupied_by_teacher.add((subject.teacher_id, day_index, period_number))
            teacher_daily_load[(subject.teacher_id, day_index)] += 1; subject_daily_count[(subject.id, day_index)] += 1
            subject_periods[subject.id].append((day_index, period_number)); remaining[subject.id] -= 1; made_assignment = True
        if not made_assignment:
            for subject in schedulable:
                if remaining[subject.id] > 0:
                    warnings.append(f"Could not place {remaining[subject.id]} period(s) of {subject.name} without a teacher clash.")
            break
    return slots, warnings
