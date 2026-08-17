import { useEffect, useRef, useState } from 'react';
import { Icon } from './ui';
import { getNotifications, markNotificationRead, type NotificationItem } from '../../services/api/notifications';

function formatTime(value: string) {
  return new Date(value).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' });
}

export function NotificationBell({ grade = '12', section = 'A' }: { grade?: string; section?: string }) {
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState<NotificationItem[]>([]);
  const [selected, setSelected] = useState<NotificationItem | null>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const unreadCount = items.filter(item => !item.read).length;

  useEffect(() => {
    let active = true;
    const load = async () => {
      const next = await getNotifications(grade, section);
      if (active) setItems(next);
    };
    void load();
    const timer = window.setInterval(load, 5000);
    return () => { active = false; window.clearInterval(timer); };
  }, [grade, section]);

  useEffect(() => {
    if (!open) return;
    const onClick = (event: MouseEvent) => {
      if (panelRef.current && !panelRef.current.contains(event.target as Node)) {
        setOpen(false);
        setSelected(null);
      }
    };
    document.addEventListener('mousedown', onClick);
    return () => document.removeEventListener('mousedown', onClick);
  }, [open]);

  const openItem = async (item: NotificationItem) => {
    setSelected(item);
    if (!item.read) {
      await markNotificationRead(item.id);
      setItems(current => current.map(entry => entry.id === item.id ? { ...entry, read: true } : entry));
    }
  };

  return (
    <div className="notification-wrap" ref={panelRef}>
      <button className="icon-btn notification-btn" onClick={() => { setOpen(value => !value); setSelected(null); }} aria-label="Notifications">
        <Icon>notifications</Icon>
        {unreadCount > 0 && <span className="notification-badge">{unreadCount}</span>}
      </button>
      {open && (
        <div className="notification-panel">
          <div className="notification-panel-head">
            <strong>Notifications</strong>
            {unreadCount > 0 && <span className="muted">{unreadCount} unread</span>}
          </div>
          {selected ? (
            <>
              <div className="notification-detail-nav">
                <button className="notification-back" onClick={() => setSelected(null)}>← Back</button>
              </div>
              <div className="notification-detail">
                <span className="notification-type">{selected.type === 'timetable' ? 'Timetable update' : selected.type}</span>
                <h3>{selected.title}</h3>
                <p>{selected.body}</p>
                <time className="notification-time">{formatTime(selected.created_at)}</time>
              </div>
            </>
          ) : items.length === 0 ? (
            <p className="notification-empty">No notifications yet.</p>
          ) : (
            <ul className="notification-list">
              {items.map(item => (
                <li key={item.id}>
                  <button className={`notification-item ${item.read ? 'read' : 'unread'}`} onClick={() => void openItem(item)}>
                    <span className="notification-item-title">{item.title}</span>
                    <span className="notification-item-preview">{item.body}</span>
                    <small className="muted">{formatTime(item.created_at)}</small>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
