import { createContext, useContext, useEffect, useMemo, useReducer, type ReactNode } from 'react';
import { request } from '../services/api/client';

export type Weekday = 'Mon' | 'Tue' | 'Wed' | 'Thu' | 'Fri';
export type SlotId = `${Weekday}-${string}`;
export interface TimetableSlot { id: SlotId; day: Weekday; time: string; subject: string | null; }
export interface TimetableState { grade: string; section: string; slots: TimetableSlot[]; dirty: boolean; saving: boolean; lastSavedAt: string | null; }
type Action = { type: 'setClass'; grade: string; section: string } | { type: 'assign'; slotId: SlotId; subject: string } | { type: 'clear'; slotId: SlotId } | { type: 'saving' } | { type: 'saved' };
export const weekdays: Weekday[] = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];
export const periods = ['09:00', '10:00', '11:30', '01:00'];
export const subjects = ['Mathematics', 'Physics', 'Chemistry', 'English', 'Computer Lab'];
function buildSlots(): TimetableSlot[] { return periods.flatMap(time => weekdays.map(day => ({ id: `${day}-${time}` as SlotId, day, time, subject: null }))); }
const initialState: TimetableState = { grade: '12', section: 'A', slots: buildSlots(), dirty: false, saving: false, lastSavedAt: null };
function reducer(state: TimetableState, action: Action): TimetableState { if (action.type === 'setClass') return { ...state, grade: action.grade, section: action.section, dirty: false }; if (action.type === 'assign') return { ...state, dirty: true, slots: state.slots.map(slot => slot.id === action.slotId ? { ...slot, subject: action.subject } : slot) }; if (action.type === 'clear') return { ...state, dirty: true, slots: state.slots.map(slot => slot.id === action.slotId ? { ...slot, subject: null } : slot) }; if (action.type === 'saving') return { ...state, saving: true }; return { ...state, saving: false, dirty: false, lastSavedAt: new Date().toISOString() }; }
const TimetableContext = createContext<{ state: TimetableState; assign: (slotId: SlotId, subject: string) => void; clear: (slotId: SlotId) => void; setClass: (grade: string, section: string) => void; save: () => Promise<void> } | null>(null);
export function TimetableProvider({ children }: { children: ReactNode }) { const [state, dispatch] = useReducer(reducer, initialState, () => { try { return JSON.parse(localStorage.getItem('edusync-timetable') || '') as TimetableState; } catch { return initialState; } }); useEffect(() => { localStorage.setItem('edusync-timetable', JSON.stringify(state)); }, [state]); const value = useMemo(() => ({ state, assign: (slotId: SlotId, subject: string) => dispatch({ type: 'assign', slotId, subject }), clear: (slotId: SlotId) => dispatch({ type: 'clear', slotId }), setClass: (grade: string, section: string) => dispatch({ type: 'setClass', grade, section }), save: async () => { dispatch({ type: 'saving' }); try { await request('/timetable', { method: 'PUT', body: JSON.stringify({ grade: state.grade, section: state.section, slots: state.slots }) }); } catch { /* Local mode remains usable when the API is offline. */ } dispatch({ type: 'saved' }); } }), [state]); return <TimetableContext.Provider value={value}>{children}</TimetableContext.Provider>; }
export function useTimetable() { const context = useContext(TimetableContext); if (!context) throw new Error('useTimetable must be used inside TimetableProvider'); return context; }
