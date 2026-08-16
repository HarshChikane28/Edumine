import { createContext, useCallback, useContext, useEffect, useMemo, useReducer, type ReactNode } from 'react';
import { request } from '../services/api/client';

export type Weekday = 'Mon' | 'Tue' | 'Wed' | 'Thu' | 'Fri';
export type SlotId = `${Weekday}-${string}`;
export interface TimetableSubject { id: string; name: string; teacher: string; weekly_periods: number; }
export interface TimetableSlot { id: SlotId; day: Weekday; time: string; subject: string | null; subject_id: string | null; teacher: string | null; }
interface ClassOption { grade: string; section: string; }
interface TimetableResponse { grade: string; section: string; slots: TimetableSlot[]; subjects: TimetableSubject[]; warnings: string[]; }
export interface TimetableState { grade: string; section: string; slots: TimetableSlot[]; subjects: TimetableSubject[]; classes: ClassOption[]; warnings: string[]; dirty: boolean; saving: boolean; loading: boolean; error: string | null; lastSavedAt: string | null; }
type Action = { type: 'setClass'; grade: string; section: string } | { type: 'hydrate'; payload: TimetableResponse } | { type: 'recommended' } | { type: 'setClasses'; classes: ClassOption[] } | { type: 'assign'; slotId: SlotId; subject: TimetableSubject } | { type: 'clear'; slotId: SlotId } | { type: 'saving' } | { type: 'saved'; payload: TimetableResponse } | { type: 'failed'; message: string };
export const weekdays: Weekday[] = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];
export const periods = ['09:00', '10:00', '11:30', '01:00'];
function buildSlots(): TimetableSlot[] { return periods.flatMap(time => weekdays.map(day => ({ id: `${day}-${time}` as SlotId, day, time, subject: null, subject_id: null, teacher: null }))); }
const initialState: TimetableState = { grade: '12', section: 'A', slots: buildSlots(), subjects: [], classes: [], warnings: [], dirty: false, saving: false, loading: true, error: null, lastSavedAt: null };
const demoSubjects: TimetableSubject[] = [
  { id: 'demo-mathematics', name: 'Mathematics', teacher: 'Ms. Priya Shah', weekly_periods: 4 },
  { id: 'demo-physics', name: 'Physics', teacher: 'Mr. Arjun Mehta', weekly_periods: 4 },
  { id: 'demo-chemistry', name: 'Chemistry', teacher: 'Dr. Neha Iyer', weekly_periods: 4 },
  { id: 'demo-english', name: 'English', teacher: 'Mrs. Kavita Rao', weekly_periods: 3 },
  { id: 'demo-computer-lab', name: 'Computer Lab', teacher: 'Mr. Rohan Das', weekly_periods: 3 },
  { id: 'demo-physical-education', name: 'Physical Education', teacher: 'Coach Aman Verma', weekly_periods: 2 },
];
function demoTimetable(grade: string, section: string): TimetableResponse { const sequence = [0, 1, 2, 3, 1, 2, 4, 0, 2, 3, 0, 5, 3, 4, 1, 2, 4, 0, 1, 5]; return { grade, section, subjects: demoSubjects, warnings: [], slots: buildSlots().map((slot, index) => { const subject = demoSubjects[sequence[index]]; return { ...slot, subject: subject.name, subject_id: subject.id, teacher: subject.teacher }; }) }; }
function reducer(state: TimetableState, action: Action): TimetableState {
  if (action.type === 'setClass') return { ...state, grade: action.grade, section: action.section, slots: buildSlots(), subjects: [], warnings: [], dirty: false, loading: true, error: null };
  if (action.type === 'setClasses') return { ...state, classes: action.classes };
  if (action.type === 'hydrate') return { ...state, ...action.payload, slots: action.payload.slots.length ? action.payload.slots : buildSlots(), dirty: false, saving: false, loading: false, error: null };
  if (action.type === 'recommended') return { ...state, dirty: true };
  if (action.type === 'assign') return { ...state, dirty: true, slots: state.slots.map(slot => slot.id === action.slotId ? { ...slot, subject: action.subject.name, subject_id: action.subject.id, teacher: action.subject.teacher } : slot) };
  if (action.type === 'clear') return { ...state, dirty: true, slots: state.slots.map(slot => slot.id === action.slotId ? { ...slot, subject: null, subject_id: null, teacher: null } : slot) };
  if (action.type === 'saving') return { ...state, saving: true, error: null };
  if (action.type === 'saved') return { ...state, ...action.payload, slots: action.payload.slots.length ? action.payload.slots : buildSlots(), saving: false, dirty: false, lastSavedAt: new Date().toISOString(), error: null };
  return { ...state, saving: false, loading: false, error: action.message };
}
const TimetableContext = createContext<{ state: TimetableState; assign: (slotId: SlotId, subjectId: string) => void; clear: (slotId: SlotId) => void; setClass: (grade: string, section: string) => void; save: () => Promise<void>; generate: () => Promise<void> } | null>(null);

export function TimetableProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState);
  const load = useCallback(async (grade: string, section: string, recommendation = false) => {
    try {
      const path = recommendation ? `/timetable/recommendation?grade=${encodeURIComponent(grade)}&section=${encodeURIComponent(section)}` : `/timetable?grade=${encodeURIComponent(grade)}&section=${encodeURIComponent(section)}`;
      const payload = await request<TimetableResponse>(path, recommendation ? { method: 'POST' } : undefined);
      dispatch({ type: 'hydrate', payload });
      if (recommendation) dispatch({ type: 'recommended' });
    } catch (error) { dispatch({ type: 'hydrate', payload: demoTimetable(grade, section) }); dispatch({ type: 'failed', message: 'Not authenticated — showing demo timetable data. Sign in with a real account to load and save the database timetable.' }); }
  }, []);
  useEffect(() => { void load(state.grade, state.section); }, [load, state.grade, state.section]);
  useEffect(() => { void request<ClassOption[]>('/timetable/classes').then(classes => dispatch({ type: 'setClasses', classes })).catch(() => dispatch({ type: 'setClasses', classes: [{ grade: '12', section: 'A' }, { grade: '11', section: 'A' }, { grade: '10', section: 'B' }] })); }, []);
  const value = useMemo(() => ({
    state,
    assign: (slotId: SlotId, subjectId: string) => { const subject = state.subjects.find(item => item.id === subjectId); if (subject) dispatch({ type: 'assign', slotId, subject }); },
    clear: (slotId: SlotId) => dispatch({ type: 'clear', slotId }),
    setClass: (grade: string, section: string) => dispatch({ type: 'setClass', grade, section }),
    generate: async () => { await load(state.grade, state.section, true); },
    save: async () => {
      dispatch({ type: 'saving' });
      try {
        const payload = await request<TimetableResponse & { saved: boolean }>('/timetable', { method: 'PUT', body: JSON.stringify({ grade: state.grade, section: state.section, slots: state.slots.map(({ day, time, subject_id }) => ({ day, time, subject_id })) }) });
        dispatch({ type: 'saved', payload });
      } catch (error) { dispatch({ type: 'failed', message: error instanceof Error ? error.message : 'The timetable was not saved. Resolve any teacher conflict and try again.' }); }
    },
  }), [load, state]);
  return <TimetableContext.Provider value={value}>{children}</TimetableContext.Provider>;
}
export function useTimetable() { const context = useContext(TimetableContext); if (!context) throw new Error('useTimetable must be used inside TimetableProvider'); return context; }
