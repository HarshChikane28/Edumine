import { useStudentProfile } from '../../lib/api/hooks';

export default function Profile() {
  const studentId = 1;
  const { data, isLoading } = useStudentProfile(studentId);

  if (isLoading) {
    return <div className="animate-pulse p-8">Loading profile...</div>;
  }

  const student = data?.student;
  const insight = data?.latest_insight;

  return (
    <div className="max-w-5xl mx-auto relative z-10 flex flex-col gap-gutter w-full">
      {/* Profile Header Card */}
      <div className="bg-surface-container-lowest rounded-3xl p-md md:p-lg shadow-[0px_4px_12px_rgba(30,41,59,0.05)] border border-[#E2E8F0] flex flex-col md:flex-row items-center md:items-start gap-md md:gap-lg relative overflow-hidden">
        <div className="absolute -top-10 -left-10 w-40 h-40 bg-primary-container/20 rounded-full blur-3xl"></div>
        <div className="relative shrink-0">
          <div className="w-24 h-24 md:w-32 md:h-32 rounded-full overflow-hidden border-4 border-surface-container-lowest shadow-sm z-10 relative">
            <img alt="Student Profile Photo" className="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCcnhOSDDOQbuxOr87_8OUr02qnqM-R0P4p1umymT7bbgiqWQvZvE8vWdtZaDDvW_NS0WWBABD4-s9vxg_rUpKeDGRj8l2TUEba4atCMuuC4kRjXMvzpzSAk04iiCbZ_Z0IEnabkIlGkBi21MHB981L5nj4uJ_S6KRjv-YzWDy4jdXtc5lwJM32xicvPStnwGPW6DaMcDVshVF49NDBksPi7ry1gC_5btULrBtv_En9yRwiWvhKzQ-5JzlZxLkC0AHx2j0" />
          </div>
          <button className="absolute bottom-0 right-0 w-8 h-8 bg-primary rounded-full flex items-center justify-center border-2 border-surface-container-lowest shadow-sm text-on-primary hover:bg-primary-container hover:text-on-primary-container transition-colors z-20">
            <span className="material-symbols-outlined text-[16px]">edit</span>
          </button>
        </div>
        <div className="flex-1 text-center md:text-left flex flex-col justify-center h-full pt-xs md:pt-md">
          <h1 className="font-headline-xl font-bold text-on-surface mb-xs">{student?.user?.full_name || 'Student Name'}</h1>
          <div className="inline-flex items-center gap-xs bg-surface-container-high text-on-surface-variant px-sm py-xs rounded-full font-label-md mb-sm w-fit mx-auto md:mx-0">
            <span>Springfield High</span>
            <span className="w-1 h-1 bg-outline rounded-full"></span>
            <span>Class - A</span>
          </div>
          <p className="text-on-surface-variant font-body-sm">ID: {student?.student_id_str || 'N/A'}</p>
        </div>
      </div>

      {/* Metrics Bento Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-gutter">
        <div className="bg-surface-container-lowest rounded-2xl p-md shadow-[0px_4px_12px_rgba(30,41,59,0.05)] border border-[#E2E8F0] flex flex-col items-center justify-center gap-xs hover:ring-2 ring-primary transition-all cursor-default">
          <div className="w-10 h-10 rounded-full bg-[#E8F5E9] text-[#2E7D32] flex items-center justify-center mb-sm">
            <span className="material-symbols-outlined">bar_chart</span>
          </div>
          <span className="font-headline-lg font-bold text-on-surface">{student?.gpa || '0.0'}</span>
          <span className="text-on-surface-variant font-label-md uppercase tracking-wider">GPA</span>
        </div>
        
        <div className="bg-surface-container-lowest rounded-2xl p-md shadow-[0px_4px_12px_rgba(30,41,59,0.05)] border border-[#E2E8F0] flex flex-col items-center justify-center gap-xs hover:ring-2 ring-[#1976D2] transition-all cursor-default">
          <div className="w-10 h-10 rounded-full bg-[#E3F2FD] text-[#1976D2] flex items-center justify-center mb-sm">
            <span className="material-symbols-outlined">pie_chart</span>
          </div>
          <span className="font-headline-lg font-bold text-on-surface">{student?.attendance_percent || '0'}%</span>
          <span className="text-on-surface-variant font-label-md uppercase tracking-wider">Attendance</span>
        </div>
        
        <div className="bg-surface-container-lowest rounded-2xl p-md shadow-[0px_4px_12px_rgba(30,41,59,0.05)] border border-[#E2E8F0] flex flex-col items-center justify-center gap-xs hover:ring-2 ring-[#F57C00] transition-all cursor-default">
          <div className="w-10 h-10 rounded-full bg-[#FFF3E0] text-[#F57C00] flex items-center justify-center mb-sm">
            <span className="material-symbols-outlined">assignment_late</span>
          </div>
          <span className="font-headline-lg font-bold text-on-surface">3 Left</span>
          <span className="text-on-surface-variant font-label-md uppercase tracking-wider">Assignments</span>
        </div>
      </div>

      {/* AI Insight Banner */}
      {insight && (
        <div className="rounded-2xl p-md md:p-lg text-on-primary shadow-md relative overflow-hidden flex flex-col gap-sm" style={{ background: 'linear-gradient(90deg, #4f378a 0%, #6750a4 100%)' }}>
          <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/4"></div>
          <div className="flex items-center gap-sm relative z-10 mb-xs">
            <span className="material-symbols-outlined text-[#ffdf93]">auto_awesome</span>
            <h3 className="font-headline-md font-bold">AI Performance Insight</h3>
          </div>
          <ul className="flex flex-col gap-xs relative z-10 font-body-sm text-primary-fixed-dim list-disc pl-md">
            <li>{insight.insight_text}</li>
          </ul>
        </div>
      )}

      {/* Expandable Sections */}
      <div className="flex flex-col gap-sm mt-md">
        <h4 className="text-center text-on-surface-variant font-headline-sm font-semibold mb-xs">Personal Details</h4>
        <button className="bg-surface-container-lowest rounded-xl p-md shadow-[0px_4px_12px_rgba(30,41,59,0.05)] border border-[#E2E8F0] flex items-center justify-between hover:bg-surface-container-low transition-colors w-full text-left">
          <div className="flex items-center gap-sm text-on-surface">
            <span className="material-symbols-outlined text-primary">person</span>
            <span className="font-body-md font-medium">View Personal Information</span>
          </div>
          <span className="material-symbols-outlined text-on-surface-variant">expand_more</span>
        </button>
      </div>
    </div>
  );
}
