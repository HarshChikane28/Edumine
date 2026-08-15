import { useEffect, useState } from 'react';
import { Login, StudentDashboard, Assignments, Profile, Result } from '../pages/student';
import { Exams, Documents, Activities, Timetable } from '../pages/admin';

export type Role = 'student' | 'admin';
export type Route = 'login' | 'dashboard' | 'assignments' | 'profile' | 'result' | 'exams' | 'documents' | 'activities' | 'timetable';
export const routePaths: Record<Route, string> = { login: '/login', dashboard: '/', assignments: '/assignments', profile: '/profile', result: '/results/semester', exams: '/admin/exams', documents: '/admin/documents', activities: '/admin/activities', timetable: '/admin/timetable' };
export function getRoute(): Route { const path = window.location.pathname; if (path.includes('/login')) return 'login'; if (path.includes('assignments')) return 'assignments'; if (path.includes('profile')) return 'profile'; if (path.includes('results')) return 'result'; if (path.includes('/admin/exams')) return 'exams'; if (path.includes('documents')) return 'documents'; if (path.includes('activities')) return 'activities'; if (path.includes('timetable')) return 'timetable'; return 'dashboard'; }
export function navigate(route: Route) { window.history.pushState({}, '', routePaths[route]); window.dispatchEvent(new PopStateEvent('popstate')); }
export function getStoredRole(): Role | null { const role = window.localStorage.getItem('edusync-role'); return role === 'student' || role === 'admin' ? role : null; }
export function setStoredRole(role: Role) { window.localStorage.setItem('edusync-role', role); }
export function clearStoredRole() { window.localStorage.removeItem('edusync-role'); }

export function App() {
  const [route, setRoute] = useState<Route>(getRoute);
  const [role, setRole] = useState<Role | null>(getStoredRole);
  useEffect(() => { const handleNavigation = () => setRoute(getRoute()); window.addEventListener('popstate', handleNavigation); return () => window.removeEventListener('popstate', handleNavigation); }, []);
  if (route === 'login' || !role) return <Login onLogin={(nextRole) => { setStoredRole(nextRole); setRole(nextRole); navigate(nextRole === 'student' ? 'dashboard' : 'activities'); }} />;
  if (role === 'student' && ['exams', 'documents', 'activities', 'timetable'].includes(route)) { navigate('dashboard'); return <StudentDashboard />; }
  if (role === 'admin' && ['dashboard', 'assignments', 'profile', 'result'].includes(route)) { navigate('activities'); return <Activities />; }
  switch (route) {
    case 'assignments': return <Assignments />;
    case 'profile': return <Profile />;
    case 'result': return <Result />;
    case 'exams': return <Exams />;
    case 'documents': return <Documents />;
    case 'activities': return <Activities />;
    case 'timetable': return <Timetable />;
    default: return <StudentDashboard />;
  }
}
