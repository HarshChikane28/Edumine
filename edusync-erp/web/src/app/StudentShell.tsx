import { Outlet, Link, useLocation } from 'react-router-dom';

export default function StudentShell() {
  const location = useLocation();
  const currentPath = location.pathname;

  return (
    <div className="text-on-background font-body-md antialiased overflow-x-hidden min-h-screen flex flex-col" style={{
      backgroundColor: '#fdf7ff',
      backgroundImage: 'radial-gradient(at 100% 0%, hsla(190, 80%, 90%, 0.4) 0px, transparent 50%), radial-gradient(at 0% 100%, hsla(340, 80%, 95%, 0.4) 0px, transparent 50%)',
      backgroundAttachment: 'fixed'
    }}>
      {/* TopNavBar */}
      <header className="sticky top-0 z-50 flex justify-between items-center px-margin-desktop py-4 w-full bg-background/80 backdrop-blur-md border-b border-outline-variant/30 shadow-sm">
        <div className="flex items-center gap-2 text-primary font-headline-xl font-bold">
          <span className="material-symbols-outlined text-3xl">import_contacts</span>
          EduSync ERP
        </div>
        <div className="flex items-center gap-4">
          <button className="p-2 rounded-full text-on-surface-variant hover:bg-primary-container/20 transition-colors scale-95 active:scale-90 transition-transform">
            <span className="material-symbols-outlined">notifications</span>
          </button>
          <button className="p-2 rounded-full text-on-surface-variant hover:bg-primary-container/20 transition-colors scale-95 active:scale-90 transition-transform">
            <span className="material-symbols-outlined">apps</span>
          </button>
          <button className="p-2 rounded-full text-on-surface-variant hover:bg-primary-container/20 transition-colors scale-95 active:scale-90 transition-transform">
            <span className="material-symbols-outlined">settings</span>
          </button>
          <img className="w-10 h-10 rounded-full border-2 border-surface object-cover shadow-sm ml-2" alt="User profile" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDJg3EUxGWc_bjJscwtVrnswkxTdplTAn-KxaAZCLZQE9JqtY8sCObty7TdkjFPL3Cj3VDzRZSKB6sndF4odWGR_jUT2Gl7fmqFv5QOQzY-9x5Gea-PKfN7FDJwKnjR0rwRuZcQqD0huMUQYaJBKJ8ulfPNrWLm166-cBKp3q5bfjGa1HhjBgHr_a8B6IuEpfL5fUGfpZh5hEkOxqtyDIIuDXHXiHwNwYKPhzKWqocIyMpaGrPbTEmckqC8szXoVmitc2o" />
        </div>
      </header>

      <div className="flex h-screen overflow-hidden">
        {/* SideNavBar */}
        <nav className="hidden lg:flex flex-col h-full w-64 rounded-r-xl border-r border-outline-variant/20 shadow-md bg-surface-container-low py-md px-base flex-shrink-0 relative z-40">
          <div className="flex items-center gap-3 mb-8 px-4">
            <div className="w-10 h-10 rounded-full bg-primary-container flex items-center justify-center text-on-primary-container font-bold">MC</div>
            <div>
              <div className="font-headline-md text-on-surface font-bold leading-tight">Main Campus</div>
              <div class="font-label-md text-on-surface-variant">Springfield High</div>
            </div>
          </div>
          <ul className="flex flex-col gap-2 flex-grow">
            <li>
              <Link to="/" className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${currentPath === '/' ? 'bg-primary-container text-on-primary-container font-semibold translate-x-1 duration-200' : 'text-on-surface-variant hover:text-primary hover:bg-surface-container-high'}`}>
                <span className={`material-symbols-outlined ${currentPath === '/' ? 'icon-fill' : ''}`}>dashboard</span>
                <span className="font-label-md">Dashboard</span>
              </Link>
            </li>
            <li>
              <Link to="/assignments" className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${currentPath === '/assignments' ? 'bg-primary-container text-on-primary-container font-semibold translate-x-1 duration-200' : 'text-on-surface-variant hover:text-primary hover:bg-surface-container-high'}`}>
                <span className={`material-symbols-outlined ${currentPath === '/assignments' ? 'icon-fill' : ''}`}>assignment</span>
                <span className="font-label-md">Assignments</span>
              </Link>
            </li>
            <li>
              <Link to="/profile" className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${currentPath === '/profile' ? 'bg-primary-container text-on-primary-container font-semibold translate-x-1 duration-200' : 'text-on-surface-variant hover:text-primary hover:bg-surface-container-high'}`}>
                <span className={`material-symbols-outlined ${currentPath === '/profile' ? 'icon-fill' : ''}`}>person</span>
                <span className="font-label-md">Profile</span>
              </Link>
            </li>
          </ul>
          <div className="mt-auto">
            <button className="w-full flex items-center justify-center gap-2 py-3 mb-4 border border-outline-variant text-primary rounded-xl font-label-md hover:bg-surface-container-high transition-colors">
                Support Center
            </button>
            <Link to="/logout" className="flex items-center gap-3 px-4 py-3 text-on-surface-variant hover:text-error hover:bg-error-container/20 rounded-xl transition-all">
              <span className="material-symbols-outlined">logout</span>
              <span className="font-label-md">Logout</span>
            </Link>
          </div>
        </nav>

        {/* Main Content Canvas */}
        <main className="flex-grow overflow-y-auto px-margin-mobile md:px-margin-desktop py-8 pb-32 lg:pb-8">
          <Outlet />
        </main>
      </div>

      {/* BottomNavBar */}
      <nav className="lg:hidden fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-4 py-3 pb-safe bg-surface/90 backdrop-blur-lg rounded-t-3xl border-t border-outline-variant/30 shadow-[0_-4px_12px_rgba(30,41,59,0.08)]">
        <Link to="/" className={`flex flex-col items-center justify-center transition-transform duration-300 p-2 rounded-xl ${currentPath === '/' ? 'text-primary active:bg-surface-variant/20 scale-110' : 'text-outline active:bg-surface-variant/20'}`}>
          <span className={`material-symbols-outlined ${currentPath === '/' ? 'icon-fill' : ''}`}>home</span>
          <span className="font-label-md mt-1">Home</span>
        </Link>
        <Link to="/assignments" className={`flex flex-col items-center justify-center transition-transform duration-300 p-2 rounded-xl ${currentPath === '/assignments' ? 'text-primary active:bg-surface-variant/20 scale-110' : 'text-outline active:bg-surface-variant/20'}`}>
          <span className={`material-symbols-outlined ${currentPath === '/assignments' ? 'icon-fill' : ''}`}>assignment_turned_in</span>
          <span className="font-label-md mt-1">Tasks</span>
        </Link>
        <Link to="/profile" className={`flex flex-col items-center justify-center transition-transform duration-300 p-2 rounded-xl ${currentPath === '/profile' ? 'text-primary active:bg-surface-variant/20 scale-110' : 'text-outline active:bg-surface-variant/20'}`}>
          <span className={`material-symbols-outlined ${currentPath === '/profile' ? 'icon-fill' : ''}`}>person</span>
          <span className="font-label-md mt-1">Profile</span>
        </Link>
      </nav>
    </div>
  );
}
