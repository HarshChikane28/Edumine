import { request } from './client';

export type NotificationItem = {
  id: string;
  title: string;
  body: string;
  type: string;
  grade: string;
  section: string;
  read: boolean;
  created_at: string;
};

const STORAGE_KEY = 'edusync-notifications';

function readLocalNotifications(grade: string, section: string): NotificationItem[] {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const items = JSON.parse(raw) as NotificationItem[];
    return items.filter(item => item.grade === grade && item.section.toUpperCase() === section.toUpperCase());
  } catch {
    return [];
  }
}

function writeLocalNotifications(items: NotificationItem[]) {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
}

export function addLocalTimetableNotification(grade: string, section: string) {
  const existing = readLocalNotifications(grade, section);
  const allRaw = window.localStorage.getItem(STORAGE_KEY);
  const all = allRaw ? (JSON.parse(allRaw) as NotificationItem[]) : [];
  const notification: NotificationItem = {
    id: `local-${Date.now()}`,
    title: 'Timetable Updated',
    body: `Your Grade ${grade} • Section ${section} timetable has been updated. Check your schedule for the latest periods.`,
    type: 'timetable',
    grade,
    section: section.toUpperCase(),
    read: false,
    created_at: new Date().toISOString(),
  };
  writeLocalNotifications([notification, ...all.filter(item => item.id !== notification.id)]);
  return [notification, ...existing];
}

export async function getNotifications(grade = '12', section = 'A') {
  try {
    return await request<NotificationItem[]>(`/notifications?grade=${encodeURIComponent(grade)}&section=${encodeURIComponent(section)}`);
  } catch {
    return readLocalNotifications(grade, section);
  }
}

export async function markNotificationRead(notificationId: string) {
  try {
    await request<{ read: boolean }>(`/notifications/${encodeURIComponent(notificationId)}/read`, { method: 'PATCH' });
  } catch {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    const items = JSON.parse(raw) as NotificationItem[];
    writeLocalNotifications(items.map(item => item.id === notificationId ? { ...item, read: true } : item));
  }
}
