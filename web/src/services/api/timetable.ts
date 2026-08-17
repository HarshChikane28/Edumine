import { request } from './client';
import { periods, weekdays, type TimetableSlot, type Weekday } from '../../stores/timetableStore';

export type TimetableView = {
  grade: string;
  section: string;
  slots: TimetableSlot[];
  warnings: string[];
};

const demoSequence = [0, 1, 2, 3, 1, 2, 4, 0, 2, 3, 0, 5, 3, 4, 1, 2, 4, 0, 1, 5];
const demoSubjects = ['Mathematics', 'English', 'Physics', 'Chemistry', 'Computer Lab', 'Physical Education'];

function buildDemoTimetable(grade: string, section: string): TimetableView {
  const slots: TimetableSlot[] = periods.flatMap(time => weekdays.map(day => ({ id: `${day}-${time}` as TimetableSlot['id'], day, time, subject: null, subject_id: null, teacher: null })));
  return {
    grade,
    section,
    warnings: [],
    slots: slots.map((slot, index) => ({ ...slot, subject: demoSubjects[demoSequence[index]] })),
  };
}

export async function getTimetable(grade = '12', section = 'A'): Promise<TimetableView> {
  try {
    const payload = await request<TimetableView>(`/timetable?grade=${encodeURIComponent(grade)}&section=${encodeURIComponent(section)}`);
    return payload;
  } catch {
    return buildDemoTimetable(grade, section);
  }
}

export function slotSubject(slots: TimetableSlot[], day: Weekday, time: string) {
  return slots.find(slot => slot.day === day && slot.time === time)?.subject || '—';
}
