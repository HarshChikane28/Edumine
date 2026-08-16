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
    } catch { dispatch({ type: 'failed', message: 'Could not load the timetable. Start the local API and run the seed script.' }); }
  }, []);
  useEffect(() => { void load(state.grade, state.section); }, [load, state.grade, state.section]);
  useEffect(() => { void request<ClassOption[]>('/timetable/classes').then(classes => dispatch({ type: 'setClasses', classes })).catch(() => undefined); }, []);
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
      } catch { dispatch({ type: 'failed', message: 'The timetable was not saved. Resolve any teacher conflict and try again.' }); }
    },
  }), [load, state]);
  return <TimetableContext.Provider value={value}>{children}</TimetableContext.Provider>;
}
export function useTimetable() { const context = useContext(TimetableContext); if (!context) throw new Error('useTimetable must be used inside TimetableProvider'); return context; }
