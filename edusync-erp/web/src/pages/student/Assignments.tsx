import { useState } from 'react';
import { useStudentAssignments } from '../../lib/api/hooks';

export default function Assignments() {
  const studentId = 1; // From auth ideally
  const [activeTab, setActiveTab] = useState<'pending' | 'submitted' | 'graded'>('pending');
  const { data, isLoading } = useStudentAssignments(studentId, activeTab);

  return (
    <div className="flex-1 max-w-5xl mx-auto w-full">
      <div className="mb-xl">
        <h1 className="font-display-lg text-primary mb-lg">Assignments</h1>
        
        {/* Tabs */}
        <div className="flex border-b border-outline-variant/30 overflow-x-auto no-scrollbar">
          {['pending', 'submitted', 'graded'].map((tab) => (
            <button 
              key={tab}
              onClick={() => setActiveTab(tab as any)}
              className={`px-xl py-sm font-headline-md capitalize whitespace-nowrap ${
                activeTab === tab 
                  ? 'text-primary font-bold border-b-2 border-primary' 
                  : 'text-on-surface-variant hover:text-primary hover:bg-surface-container/50 transition-colors'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Assignment Cards List */}
      <div className="flex flex-col gap-gutter">
        {isLoading ? (
          <div className="animate-pulse space-y-4">
            <div className="h-32 bg-surface-variant/50 rounded-xl"></div>
            <div className="h-32 bg-surface-variant/50 rounded-xl"></div>
          </div>
        ) : data && data.length > 0 ? (
          data.map((assignment: any) => (
            <div key={assignment.id} className="bg-surface-container-lowest rounded-xl p-md shadow-[0px_4px_12px_rgba(30,41,59,0.05)] border border-outline-variant/20 flex flex-col gap-md transition-shadow hover:shadow-md">
              {/* Header */}
              <div className="flex justify-between items-start">
                <div className="bg-primary-fixed text-on-primary-fixed-variant px-3 py-1 rounded-full font-label-md inline-block">
                  {assignment.subject}
                </div>
                <div className="flex items-center gap-1 text-on-surface-variant font-label-md">
                  <span className="material-symbols-outlined text-[16px]">schedule</span>
                  {activeTab === 'pending' ? 'Due Soon' : activeTab}
                </div>
              </div>
              
              {/* Title */}
              <div>
                <h3 className="font-headline-lg text-on-surface">{assignment.title}</h3>
              </div>
              
              <hr className="border-outline-variant/20" />
              
              {/* Footer */}
              <div className="flex justify-between items-center pt-sm">
                <div className="text-on-surface-variant font-body-sm">
                  Due: {new Date(assignment.due_at).toLocaleDateString()}
                </div>
                {activeTab === 'pending' ? (
                  <button className="bg-primary text-on-primary font-label-md px-6 py-2 rounded-lg hover:bg-primary/90 transition-colors">
                    Submit
                  </button>
                ) : (
                  <button className="bg-surface-variant text-on-surface-variant font-label-md px-6 py-2 rounded-lg hover:bg-surface-variant/80 transition-colors border border-outline-variant/30">
                    View Details
                  </button>
                )}
              </div>
            </div>
          ))
        ) : (
          <div className="p-8 border border-outline-variant/20 rounded-xl text-on-surface-variant bg-surface-container-lowest text-center">
            No assignments found for status: {activeTab}
          </div>
        )}
      </div>
      
      {/* Floating Action Button */}
      <button className="fixed bottom-24 right-4 md:bottom-8 md:right-8 lg:bottom-12 lg:right-12 bg-primary text-on-primary rounded-full px-6 py-4 shadow-lg hover:shadow-xl hover:bg-primary/90 transition-all flex items-center gap-2 z-40 group">
        <span className="material-symbols-outlined group-hover:rotate-90 transition-transform duration-300">add</span>
        <span className="font-label-md font-bold">New Assignment</span>
      </button>
    </div>
  );
}
