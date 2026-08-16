import { useEffect, useState } from 'react';
import { Login, StudentDashboard, Assignments, Profile, Result } from '../pages/student';
import { Exams, Documents, Activities, Timetable, TeacherManagement } from '../pages/admin';
import { TimetableProvider } from '../stores/timetableStore';

export type Role = 'student' | 'teacher' | 'admin';
export type Route = 'login' | 'dashboard' | 'assignments' | 'profile' | 'result' | 'exams' | 'documents' | 'activities' | 'timetable' | 'teacher-management';
export const routePaths: Record<Route, string> = { login: '/login', dashboard: '/', assignments: '/assignments', profile: '/profile', result: '/results/semester', exams: '/admin/exams', documents: '/admin/documents', activities: '/admin/activities', timetable: '/admin/timetable', 'teacher-management': '/admin/teachers' };
export function getRoute(): Route { const path = window.location.pathname; if (path.includes('/login')) return 'login'; if (path.includes('assignments')) return 'assignments'; if (path.includes('profile')) return 'profile'; if (path.includes('results')) return 'result'; if (path.includes('/admin/exams')) return 'exams'; if (path.includes('documents')) return 'documents'; if (path.includes('activities')) return 'activities'; if (path.includes('timetable')) return 'timetable'; if (path.includes('/admin/teachers')) return 'teacher-management'; return 'dashboard'; }
export function navigate(route: Route) { window.history.pushState({}, '', routePaths[route]); window.dispatchEvent(new PopStateEvent('popstate')); }
export function getStoredRole(): Role | null { const role = window.localStorage.getItem('edusync-role'); return role === 'student' || role === 'teacher' || role === 'admin' ? role : null; }
export function setStoredRole(role: Role) { window.localStorage.setItem('edusync-role', role); }
export function clearStoredRole() { window.localStorage.removeItem('edusync-role'); }
export function getStoredPermissions(): string[] { try { return JSON.parse(window.localStorage.getItem('edusync-permissions') || '[]'); } catch { return []; } }
export function setStoredPermissions(permissions: string[]) { window.localStorage.setItem('edusync-permissions', JSON.stringify(permissions)); }

export function App() {
  const [route, setRoute] = useState<Route>(getRoute);
  const [role, setRole] = useState<Role | null>(getStoredRole);
  useEffect(() => { const handleNavigation = () => setRoute(getRoute()); window.addEventListener('popstate', handleNavigation); return () => window.removeEventListener('popstate', handleNavigation); }, []);
  if (route === 'login' || !role) return <Login onLogin={(nextRole, permissions) => { setStoredRole(nextRole); setStoredPermissions(permissions); setRole(nextRole); navigate(nextRole === 'student' ? 'dashboard' : 'activities'); }} />;
  if (role === 'student' && ['exams', 'documents', 'activities', 'timetable'].includes(route)) { navigate('dashboard'); return <StudentDashboard />; }
  if (role !== 'student' && ['dashboard', 'assignments', 'profile', 'result'].includes(route)) { navigate('activities'); return <Activities />; }
  if (role !== 'admin' && route === 'teacher-management') { navigate('activities'); return <Activities />; }
  const page = (() => { switch (route) {
    case 'assignments': return <Assignments />;
    case 'profile': return <Profile />;
    case 'result': return <Result />;
    case 'exams': return <Exams />;
    case 'documents': return <Documents />;
    case 'activities': return <Activities />;
    case 'timetable': return <Timetable />;
    case 'teacher-management': return <TeacherManagement />;
    default: return <StudentDashboard />;
  } })();
  return <TimetableProvider>{page}</TimetableProvider>;
}
