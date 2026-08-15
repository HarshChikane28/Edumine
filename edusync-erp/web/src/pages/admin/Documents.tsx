import { useQuery } from '@tanstack/react-query';
import api from '../../lib/api/client';

export default function Documents() {
  const { data, isLoading } = useQuery({
    queryKey: ['admin', 'documents'],
    queryFn: async () => {
      // Return mock data for documents
      return {
        documents: [
          { id: 1, name: 'Student Enrollment Forms (Grade 9)', category: 'Admissions', date: '2023-10-26', requestor: 'Alex Melan', status: 'completed' },
          { id: 2, name: 'Teacher Leave Request - Sarah J.', category: 'HR / Staff', date: '2023-10-25', requestor: 'Sarah Johnson', status: 'processing' },
          { id: 3, name: 'Exam Schedule - Midterm 2023', category: 'Exams', date: '2023-10-24', requestor: 'Exam Committee', status: 'pending' },
          { id: 4, name: 'Budget Proposal for Science Lab', category: 'Finance', date: '2023-10-23', requestor: 'Dr. A. Chemist', status: 'pending' },
          { id: 5, name: 'Incident Report #452', category: 'Student Affairs', date: '2023-10-20', requestor: 'Mr. B. Dean', status: 'completed' }
        ]
      };
    }
  });

  const getStatusBadge = (status: string) => {
    switch(status.toLowerCase()) {
      case 'completed':
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full font-label-md text-[11px] font-bold bg-[#d1fae5] text-[#065f46]">Completed</span>;
      case 'processing':
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full font-label-md text-[11px] font-bold bg-[#dbeafe] text-[#1e40af]">Processing</span>;
      default:
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full font-label-md text-[11px] font-bold bg-[#fef3c7] text-[#92400e]">Pending</span>;
    }
  }

  if (isLoading) {
    return <div className="p-8 animate-pulse">Loading documents...</div>;
  }

  return (
    <div className="max-w-7xl mx-auto space-y-lg">
      <div className="flex justify-between items-center mb-md">
        <h1 className="font-headline-xl text-on-surface">Digitized Documents Requests</h1>
        <div className="flex gap-2">
          <button className="bg-[#e97b4d] text-white rounded-full py-2.5 px-6 flex items-center justify-center gap-2 font-label-md font-bold hover:opacity-90 transition-opacity shadow-sm">
            <span className="material-symbols-outlined text-lg">upload</span>
            Upload New Document
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-outline-variant shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-surface-container-lowest border-b border-outline-variant">
                <th className="py-3 px-md font-label-md text-on-surface-variant uppercase tracking-wider font-semibold w-1/4">Document Name</th>
                <th className="py-3 px-md font-label-md text-on-surface-variant uppercase tracking-wider font-semibold w-1/6">Category</th>
                <th className="py-3 px-md font-label-md text-on-surface-variant uppercase tracking-wider font-semibold w-1/6">Date Requested</th>
                <th className="py-3 px-md font-label-md text-on-surface-variant uppercase tracking-wider font-semibold w-1/6">Requestor</th>
                <th className="py-3 px-md font-label-md text-on-surface-variant uppercase tracking-wider font-semibold w-1/12 text-center">Status</th>
                <th className="py-3 px-md font-label-md text-on-surface-variant uppercase tracking-wider font-semibold w-1/12 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant bg-white">
              {data?.documents.map((doc: any) => (
                <tr key={doc.id} className="hover:bg-surface-container-lowest transition-colors group">
                  <td className="py-4 px-md font-body-sm text-on-surface font-medium">{doc.name}</td>
                  <td className="py-4 px-md font-body-sm text-on-surface-variant">{doc.category}</td>
                  <td className="py-4 px-md font-body-sm text-on-surface-variant">{new Date(doc.date).toLocaleDateString()}</td>
                  <td className="py-4 px-md font-body-sm text-on-surface-variant">{doc.requestor}</td>
                  <td className="py-4 px-md text-center">
                    {getStatusBadge(doc.status)}
                  </td>
                  <td className="py-4 px-md text-right">
                    <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button className="text-on-surface-variant hover:text-primary transition-colors p-1" title="View">
                        <span className="material-symbols-outlined text-[20px]">visibility</span>
                      </button>
                      <button className="text-on-surface-variant hover:text-primary transition-colors p-1" title="Download">
                        <span className="material-symbols-outlined text-[20px]">download</span>
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
