import { useQuery } from '@tanstack/react-query';
import api from '../../lib/api/client';

export default function Activities() {
  const { data, isLoading } = useQuery({
    queryKey: ['admin', 'activities'],
    queryFn: async () => {
      // Mock data for activities
      return {
        events: [
          { id: 1, name: 'Debate Club', date: 'Oct 27', supervisor: 'Mrs. Chen', enrollment: '45/50', icon: 'gavel', color: 'secondary' },
          { id: 2, name: 'Soccer Match: Varsity vs. Oakwood', date: 'Oct 28, 4:00 PM', supervisor: 'Mr. Davis', enrollment: '22/25', icon: 'sports_soccer', color: 'primary' },
          { id: 3, name: 'Art Exhibition Setup', date: 'Oct 29', supervisor: 'Ms. Lee', enrollment: '18/20', icon: 'palette', color: 'error' },
          { id: 4, name: 'Vremniers Club', date: 'Oct 27', supervisor: 'Ms. Lee', enrollment: '18/20', icon: 'emoji_events', color: 'tertiary' }
        ],
        top_clubs: [
          { id: 1, name: 'Robotics Club', performance: '98%', awards: 3, icon: 'precision_manufacturing', color: 'primary' },
          { id: 2, name: 'Drama Club', performance: '95%', awards: 2, icon: 'theater_comedy', color: 'secondary' }
        ],
        feed: [
          { id: 1, text: 'Science Club submitted project report', time: 'Today, 10:30 AM', type: 'primary' },
          { id: 2, text: 'New Chess Club members registered', time: 'Yesterday, 3:15 PM', type: 'neutral' },
          { id: 3, text: 'Basketball practice scheduled', time: 'Yesterday, 1:00 PM', type: 'neutral' }
        ]
      };
    }
  });

  if (isLoading) {
    return <div className="p-8 animate-pulse">Loading activities...</div>;
  }

  return (
    <div className="max-w-[1400px] mx-auto space-y-8">
      <div className="flex items-center gap-4">
        <h2 className="font-headline-xl text-on-surface">Student Activities Dashboard</h2>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-gutter">
        {/* Left/Main Column */}
        <div className="xl:col-span-8 flex flex-col gap-8">
          
          <section>
            <h3 className="font-headline-md text-on-surface mb-4">Upcoming Events & Clubs</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {data?.events.map((event: any) => (
                <div key={event.id} className="bg-surface rounded-xl p-md shadow-sm border border-outline-variant hover:border-primary transition-colors">
                  <div className="flex items-center gap-3 mb-4">
                    <div className={`w-10 h-10 rounded-full bg-${event.color}-container flex items-center justify-center text-on-${event.color}-container`}>
                      <span className="material-symbols-outlined">{event.icon}</span>
                    </div>
                    <h4 className="font-headline-sm text-[16px] font-semibold text-on-surface leading-tight">{event.name}</h4>
                  </div>
                  <div className="space-y-2 font-body-sm text-on-surface-variant">
                    <p><span className="font-semibold text-on-surface">{event.date.includes('PM') ? 'Date:' : 'Next:'}</span> {event.date}</p>
                    <p><span className="font-semibold text-on-surface">{event.icon === 'sports_soccer' ? 'Coach:' : 'Supervisor:'}</span> {event.supervisor}</p>
                    <p><span className="font-semibold text-on-surface">Enrollment:</span> {event.enrollment}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section>
            <h3 className="font-headline-md text-on-surface mb-4">Top Performing Clubs</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {data?.top_clubs.map((club: any) => (
                <div key={club.id} className="bg-surface rounded-xl p-md shadow-sm border border-outline-variant">
                  <div className="flex items-center gap-3 mb-4 border-b border-outline-variant pb-3">
                    <div className={`w-8 h-8 rounded bg-${club.color}-container flex items-center justify-center text-on-${club.color}-container`}>
                      <span className="material-symbols-outlined text-sm">{club.icon}</span>
                    </div>
                    <h4 className="font-headline-sm text-[16px] font-semibold text-on-surface">{club.name}</h4>
                  </div>
                  <div className="flex justify-between font-body-sm">
                    <span className="text-on-surface-variant">Performance:</span>
                    <span className="font-semibold text-on-surface">{club.performance}</span>
                  </div>
                  <div className="flex justify-between font-body-sm mt-2">
                    <span className="text-on-surface-variant">Awards:</span>
                    <span className="font-semibold text-on-surface">{club.awards}</span>
                  </div>
                </div>
              ))}
            </div>
          </section>

        </div>

        {/* Right Column: Recent Activity Feed */}
        <div className="xl:col-span-4">
          <div className="bg-surface rounded-xl p-md shadow-sm border border-outline-variant h-full">
            <h3 className="font-headline-md text-on-surface mb-6">Recent Activity Feed</h3>
            <div className="relative border-l-2 border-surface-variant ml-4 space-y-8">
              {data?.feed.map((item: any, idx: number) => (
                <div key={item.id} className="relative pl-6">
                  <div className={`absolute w-4 h-4 rounded-full border-2 border-surface -left-[9px] top-1 ${item.type === 'primary' ? 'bg-primary-container' : 'bg-outline-variant'}`}></div>
                  <p className="font-body-md text-on-surface">{item.text}</p>
                  <p className="font-body-sm text-on-surface-variant mt-1">{item.time}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
