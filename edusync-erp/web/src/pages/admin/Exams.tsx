import { useQuery } from '@tanstack/react-query';
import api from '../../lib/api/client';

export default function Exams() {
  const { data, isLoading } = useQuery({
    queryKey: ['admin', 'exams'],
    queryFn: async () => {
      // Mocking for now since we didn't add a specific admin dashboard endpoint
      // The API has /api/v1/exams, let's just fetch that or return mock data.
      return {
        summary: {
          upcoming: 45,
          avg_score: 78,
          grading_progress: 60
        },
        exams: [
          { id: 1, subject: 'Mathematics', date: '2023-10-26T00:00:00Z', hall: 'Hall A', proctor: 'Sarah Johnson', status: 'Scheduled' },
          { id: 2, subject: 'Physics', date: '2023-10-28T00:00:00Z', hall: 'Hall B', proctor: 'Michael Chen', status: 'Scheduled' },
          { id: 3, subject: 'Chemistry', date: '2023-10-30T00:00:00Z', hall: 'Hall C', proctor: 'Emily Davis', status: 'Scheduled' }
        ]
      };
    }
  });

  if (isLoading) {
    return <div className="p-8 animate-pulse">Loading exams...</div>;
  }

  return (
    <div className="max-w-7xl mx-auto space-y-lg">
      <div className="flex items-center gap-sm">
        <h1 className="font-headline-xl text-on-surface">Exam and Results Management</h1>
      </div>

      <section>
        <h2 className="font-headline-md text-on-surface mb-sm">Summary</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-gutter">
          <div className="bg-surface rounded-xl p-md border border-outline-variant shadow-sm flex flex-col justify-between min-h-[140px]">
            <div className="w-10 h-10 rounded-full bg-secondary-container flex items-center justify-center text-on-secondary-container mb-sm">
              <span className="material-symbols-outlined">calendar_today</span>
            </div>
            <div>
              <p className="font-body-sm text-on-surface-variant mb-1">Upcoming Exams</p>
              <p className="font-display-lg text-on-surface leading-none">{data?.summary.upcoming}</p>
            </div>
          </div>
          
          <div className="bg-surface rounded-xl p-md border border-outline-variant shadow-sm flex flex-col justify-between min-h-[140px]">
            <div className="w-10 h-10 rounded-full bg-tertiary-container flex items-center justify-center text-on-tertiary-container mb-sm">
              <span className="material-symbols-outlined">bar_chart</span>
            </div>
            <div>
              <p className="font-body-sm text-on-surface-variant mb-1">Average Score</p>
              <p className="font-display-lg text-on-surface leading-none">{data?.summary.avg_score}%</p>
            </div>
          </div>
          
          <div className="bg-surface rounded-xl p-md border border-outline-variant shadow-sm flex flex-col justify-between min-h-[140px]">
            <div className="w-10 h-10 rounded-full bg-surface-variant flex items-center justify-center text-on-surface-variant mb-sm">
              <span className="material-symbols-outlined">layers</span>
            </div>
            <div>
              <p className="font-body-sm text-on-surface-variant mb-1">Paper Grading Progress</p>
              <p className="font-headline-xl text-on-surface leading-none">{data?.summary.grading_progress}% Completed</p>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-surface rounded-xl border border-outline-variant shadow-sm overflow-hidden">
        <div className="p-md border-b border-outline-variant flex justify-between items-center">
          <h2 className="font-headline-md text-on-surface">Upcoming Examinations</h2>
          <button className="text-primary font-label-md hover:underline">View All</button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-outline-variant bg-surface-container-lowest">
                <th className="py-sm px-md font-label-md text-on-surface-variant font-semibold">Subject</th>
                <th className="py-sm px-md font-label-md text-on-surface-variant font-semibold">Date</th>
                <th className="py-sm px-md font-label-md text-on-surface-variant font-semibold">Hall Number</th>
                <th className="py-sm px-md font-label-md text-on-surface-variant font-semibold">Proctor Name</th>
                <th className="py-sm px-md font-label-md text-on-surface-variant font-semibold">Status</th>
              </tr>
            </thead>
            <tbody className="font-body-sm text-on-surface">
              {data?.exams.map((exam: any) => (
                <tr key={exam.id} className="border-b border-outline-variant hover:bg-surface-container-lowest transition-colors">
                  <td className="py-sm px-md">{exam.subject}</td>
                  <td className="py-sm px-md">{new Date(exam.date).toLocaleDateString()}</td>
                  <td className="py-sm px-md">{exam.hall}</td>
                  <td className="py-sm px-md">{exam.proctor}</td>
                  <td className="py-sm px-md">
                    <span className="inline-flex items-center px-2 py-1 rounded-full bg-secondary-container text-on-secondary-container text-[10px] font-bold uppercase tracking-wider">
                      {exam.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
