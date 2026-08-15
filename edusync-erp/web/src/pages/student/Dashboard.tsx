import { useStudentDashboard } from '../../lib/api/hooks';

export default function Dashboard() {
  const studentId = 1; // Assuming student ID 1 for now, ideally derived from auth context
  const { data, isLoading, error } = useStudentDashboard(studentId);

  if (isLoading) {
    return <div className="p-8 text-on-surface-variant animate-pulse">Loading dashboard...</div>;
  }

  if (error) {
    return <div className="p-8 text-error">Failed to load dashboard. Make sure backend is running.</div>;
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Greeting */}
      <div>
        <h1 className="font-display-lg text-on-surface">
          Hello, {data?.student?.user?.full_name || 'Student'}!
        </h1>
        <p className="font-body-lg text-on-surface-variant mt-2">
          Here's your academic overview for today.
        </p>
      </div>

      {/* Bento Grid Layout */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-gutter">
        
        {/* Events Countdown Column */}
        <div className="col-span-1 md:col-span-7 space-y-4">
          <h2 className="font-headline-md text-on-surface mb-2">Upcoming Events</h2>
          
          {data?.upcoming_events && data.upcoming_events.length > 0 ? (
            data.upcoming_events.map((event: any, i: number) => (
              <div key={i} className="bg-surface-container-lowest rounded-xl p-md shadow-[0_4px_12px_rgba(30,41,59,0.05)] border border-outline-variant/20 flex items-center justify-between hover:ring-2 ring-primary/20 transition-all cursor-pointer group">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-tertiary-fixed flex items-center justify-center text-on-tertiary-fixed group-hover:scale-110 transition-transform">
                    <span className="material-symbols-outlined">celebration</span>
                  </div>
                  <div>
                    <div className="font-label-md text-outline">Event Countdown</div>
                    <div className="font-headline-md text-on-surface leading-tight">
                      {event.title}
                    </div>
                  </div>
                </div>
                <span className="material-symbols-outlined text-outline-variant group-hover:text-primary transition-colors">chevron_right</span>
              </div>
            ))
          ) : (
            <div className="p-4 border border-outline-variant/20 rounded-xl text-on-surface-variant bg-surface-container-lowest text-center">
              No upcoming events scheduled.
            </div>
          )}
        </div>

        {/* Updates & Track Bus Column */}
        <div className="col-span-1 md:col-span-5 space-y-gutter flex flex-col">
          
          {/* Important Update Card */}
          {data?.announcements && data.announcements.length > 0 ? (
            data.announcements.map((ann: any, i: number) => (
              <div key={i} className="relative overflow-hidden rounded-xl p-md shadow-md flex-grow min-h-[200px] mb-4" style={{ background: 'linear-gradient(135deg, #fca5a5 0%, #93c5fd 100%)' }}>
                <div className="relative z-10 flex flex-col h-full justify-between">
                  <div className="w-10 h-10 rounded-full bg-white/30 backdrop-blur-sm flex items-center justify-center text-white mb-4">
                    <span className="material-symbols-outlined icon-fill">campaign</span>
                  </div>
                  <div>
                    <h3 className="font-headline-md text-surface-container-lowest font-bold">
                      {ann.title}
                    </h3>
                    <p className="font-body-sm text-surface-container-lowest/80 mt-1 mb-4">
                      {ann.body}
                    </p>
                    <button className="bg-surface-container-lowest text-primary font-label-md px-4 py-2 rounded-full shadow-sm hover:bg-surface-variant transition-colors flex items-center gap-1 w-max">
                      Read More <span className="material-symbols-outlined text-sm">arrow_forward</span>
                    </button>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="p-4 border border-outline-variant/20 rounded-xl text-on-surface-variant bg-surface-container-lowest text-center">
              No new announcements.
            </div>
          )}

        </div>
      </div>

      {/* Progress Section */}
      <div>
        <h2 className="font-headline-md text-on-surface mb-4">My Progress</h2>
        <div className="bg-surface-container-lowest rounded-xl p-md shadow-[0_4px_12px_rgba(30,41,59,0.05)] border border-outline-variant/20 h-32 flex items-center justify-center text-outline-variant">
          <span className="material-symbols-outlined mr-2">insights</span> 
          Current GPA: {data?.student?.gpa || 'N/A'} - Attendance: {data?.student?.attendance_percent || 0}%
        </div>
      </div>
    </div>
  );
}
