import { request } from './client';

export type AttendanceRecord = {
  id: string;
  date: string;
  status: 'present' | 'late' | 'absent';
  source: string;
  scan_uid: string | null;
  scanned_at: string | null;
  notes: string | null;
};

export type AttendanceOverview = {
  student_id: string;
  student_name: string;
  student_code: string;
  roll_no: string;
  grade: string;
  section: string;
  attendance_percentage: number;
  present_days: number;
  late_days: number;
  recorded_days: number;
  today_status: 'present' | 'late' | 'absent' | 'not_marked';
  latest_scan_at: string | null;
  records: AttendanceRecord[];
};

export type AttendanceCard = {
  uid: string;
  label: string | null;
  student_name: string;
  student_code: string;
  grade: string;
  section: string;
  active: boolean;
};

const today = new Date();
const daysAgo = (days: number) => {
  const value = new Date(today);
  value.setDate(today.getDate() - days);
  return value.toISOString();
};
const dateAgo = (days: number) => daysAgo(days).slice(0, 10);

export const demoAttendanceCards: AttendanceCard[] = [
  { uid: 'DEMO-NFC-001', label: 'Demo NFC Card - Demo Student', student_name: 'Demo Student', student_code: 'STU-DEMO-001', grade: 'Grade 12', section: 'A', active: true },
  { uid: 'DEMO-NFC-002', label: 'Demo NFC Card - Aarav Sharma', student_name: 'Aarav Sharma', student_code: 'STU-DEMO-002', grade: 'Grade 12', section: 'A', active: true },
  { uid: 'DEMO-NFC-003', label: 'Demo NFC Card - Isha Patel', student_name: 'Isha Patel', student_code: 'STU-DEMO-003', grade: 'Grade 12', section: 'A', active: true },
  { uid: 'DEMO-NFC-004', label: 'Demo NFC Card - Kabir Khan', student_name: 'Kabir Khan', student_code: 'STU-DEMO-004', grade: 'Grade 11', section: 'A', active: true },
  { uid: 'DEMO-NFC-005', label: 'Demo NFC Card - Meera Nair', student_name: 'Meera Nair', student_code: 'STU-DEMO-005', grade: 'Grade 10', section: 'B', active: true },
];

export const demoAttendanceRecords: AttendanceOverview[] = demoAttendanceCards.map((card, index) => {
  const records: AttendanceRecord[] = [
    { id: `${card.uid}-6`, date: dateAgo(6), status: 'present', source: 'demo', scan_uid: card.uid, scanned_at: daysAgo(6), notes: 'Demo attendance history' },
    { id: `${card.uid}-5`, date: dateAgo(5), status: 'late', source: 'demo', scan_uid: card.uid, scanned_at: daysAgo(5), notes: 'Demo attendance history' },
    { id: `${card.uid}-4`, date: dateAgo(4), status: 'present', source: 'demo', scan_uid: card.uid, scanned_at: daysAgo(4), notes: 'Demo attendance history' },
    { id: `${card.uid}-3`, date: dateAgo(3), status: 'absent', source: 'demo', scan_uid: null, scanned_at: daysAgo(3), notes: 'Demo attendance history' },
    { id: `${card.uid}-2`, date: dateAgo(2), status: 'present', source: 'demo', scan_uid: card.uid, scanned_at: daysAgo(2), notes: 'Demo attendance history' },
    { id: `${card.uid}-1`, date: dateAgo(1), status: 'present', source: 'demo', scan_uid: card.uid, scanned_at: daysAgo(1), notes: 'Demo attendance history' },
  ];
  const presentDays = records.filter(record => record.status === 'present').length;
  const lateDays = records.filter(record => record.status === 'late').length;
  return { student_id: `demo-${index + 1}`, student_name: card.student_name, student_code: card.student_code, roll_no: `${index + 1}`, grade: card.grade, section: card.section, attendance_percentage: Math.round(((presentDays + lateDays) / records.length) * 100), present_days: presentDays, late_days: lateDays, recorded_days: records.length, today_status: 'not_marked', latest_scan_at: records[0].scanned_at, records };
});

export function applyDemoScan(cardUid: string) {
  const card = demoAttendanceCards.find(item => item.uid === cardUid);
  const student = demoAttendanceRecords.find(item => item.student_code === card?.student_code);
  if (!card || !student) throw new Error('Demo NFC card not found');
  const scannedAt = new Date().toISOString();
  const todayDate = scannedAt.slice(0, 10);
  const existing = student.records.find(record => record.date === todayDate);
  if (existing) {
    existing.status = 'present';
    existing.scanned_at = scannedAt;
    existing.scan_uid = cardUid;
    existing.notes = 'Demo scan updated from UI';
  } else {
    student.records.unshift({ id: `${cardUid}-today`, date: todayDate, status: 'present', source: 'demo', scan_uid: cardUid, scanned_at: scannedAt, notes: 'Demo scan recorded from UI' });
  }
  student.today_status = 'present';
  student.latest_scan_at = scannedAt;
  student.present_days = student.records.filter(record => record.status === 'present').length;
  student.late_days = student.records.filter(record => record.status === 'late').length;
  student.recorded_days = student.records.length;
  student.attendance_percentage = Math.round(((student.present_days + student.late_days) / student.recorded_days) * 100);
  return student;
}

export async function getAttendanceOverview(studentCode = 'STU-DEMO-001') {
  return request<AttendanceOverview>(`/attendance/overview?student_code=${encodeURIComponent(studentCode)}`);
}

export async function getAttendanceRecords() {
  return request<AttendanceOverview[]>('/attendance/records');
}

export async function getAttendanceCards() {
  return request<AttendanceCard[]>('/attendance/cards');
}

export async function scanAttendance(cardUid: string, deviceLabel = 'Mobile NFC') {
  return request<{ recorded: boolean; created: boolean; message: string; attendance: AttendanceOverview }>('/attendance/scan', { method: 'POST', body: JSON.stringify({ card_uid: cardUid, device_label: deviceLabel }) });
}
