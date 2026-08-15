import { Outlet, Link, useLocation } from 'react-router-dom';

export default function AdminShell() {
  const location = useLocation();

  const navLinks = [
    { name: 'Dashboard', path: '/admin', icon: 'dashboard' },
    { name: 'Exams', path: '/admin/exams', icon: 'assignment' },
    { name: 'Timetable', path: '/admin/timetable', icon: 'calendar_month' },
    { name: 'Activities', path: '/admin/activities', icon: 'celebration' },
    { name: 'Documents', path: '/admin/documents', icon: 'folder' },
  ];

  return (
    <div className="bg-background text-on-surface antialiased flex min-h-screen">
      {/* SideNavBar (Desktop) */}
      <nav className="hidden lg:flex flex-col h-screen py-md px-base bg-surface-container-low dark:bg-surface-container text-primary dark:text-primary-fixed font-label-md fixed left-0 w-64 rounded-r-xl border-r border-outline-variant/20 shadow-md z-40">
        <div className="flex items-center gap-sm mb-lg px-base">
          <div className="w-10 h-10 rounded-full bg-primary-container flex items-center justify-center overflow-hidden">
            <span className="material-symbols-outlined text-on-primary-container">admin_panel_settings</span>
          </div>
          <div>
            <h2 className="font-headline-md font-bold text-on-surface">EduSync Admin</h2>
            <p className="text-on-surface-variant font-body-sm">Main Campus</p>
          </div>
        </div>

        <ul className="flex-1 space-y-sm">
          {navLinks.map((link) => {
            const isActive = location.pathname === link.path || (link.path !== '/admin' && location.pathname.startsWith(link.path));
            return (
              <li key={link.name}>
                <Link
                  to={link.path}
                  className={`flex items-center gap-md px-sm py-sm rounded-xl transition-all duration-200 ${
                    isActive
                      ? 'bg-primary-container text-on-primary-container font-semibold translate-x-1'
                      : 'text-on-surface-variant hover:text-primary hover:bg-surface-container-high translate-x-1'
                  }`}
                >
                  <span className={`material-symbols-outlined ${isActive ? 'icon-fill' : ''}`}>{link.icon}</span>
                  <span>{link.name}</span>
                </Link>
              </li>
            );
          })}
        </ul>

        <div className="mt-auto pt-md border-t border-outline-variant/20">
          <Link to="/" className="flex items-center gap-md px-sm py-sm text-on-surface-variant hover:text-error hover:bg-error-container/20 rounded-xl transition-all">
            <span className="material-symbols-outlined">logout</span>
            <span>Logout</span>
          </Link>
        </div>
      </nav>

      {/* Main Content Canvas */}
      <main className="flex-1 flex flex-col lg:ml-64 min-h-screen">
        {/* TopNavBar */}
        <header className="sticky top-0 z-50 flex justify-between items-center px-margin-desktop py-4 w-full bg-background/80 backdrop-blur-md shadow-sm border-b border-outline-variant/30">
          <div className="flex items-center gap-sm">
            <button className="lg:hidden p-2 text-on-surface-variant rounded-full hover:bg-surface-container-highest transition-colors">
              <span className="material-symbols-outlined">menu</span>
            </button>
            <div className="font-headline-xl font-bold text-primary lg:hidden flex items-center gap-2">
              <span className="material-symbols-outlined text-3xl">menu_book</span>
              EduSync
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className="ml-2 w-10 h-10 rounded-full bg-primary text-on-primary flex items-center justify-center font-bold shadow-sm">
              AD
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 p-margin-mobile md:p-margin-desktop pb-32 lg:pb-margin-desktop bg-surface-container-lowest">
          <Outlet />
        </div>
      </main>

      {/* BottomNavBar (Mobile) */}
      <nav className="lg:hidden fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-4 py-3 pb-safe bg-surface/90 backdrop-blur-lg rounded-t-3xl shadow-[0_-4px_12px_rgba(30,41,59,0.08)] border-t border-outline-variant/30 text-primary font-label-md text-label-md">
        {navLinks.map((link) => {
          const isActive = location.pathname === link.path || (link.path !== '/admin' && location.pathname.startsWith(link.path));
          return (
            <Link
              key={link.name}
              to={link.path}
              className={`flex flex-col items-center justify-center p-2 rounded-xl ${
                isActive ? 'text-primary' : 'text-outline hover:bg-surface-variant/20'
              }`}
            >
              <span className={`material-symbols-outlined ${isActive ? 'icon-fill' : ''}`}>{link.icon}</span>
              <span className="mt-1 text-[10px]">{link.name}</span>
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
