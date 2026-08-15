import { useStudentResults } from '../../lib/api/hooks';
import { useParams, Link } from 'react-router-dom';

export default function Results() {
  const studentId = 1; // From Auth context ideally
  const { examId } = useParams();
  
  // Assuming examId is optionally parsed from URL or default fetched
  const { data, isLoading } = useStudentResults(studentId, examId ? parseInt(examId) : undefined);

  if (isLoading) {
    return <div className="animate-pulse p-8">Loading results...</div>;
  }

  const result = data?.result;
  const scores = data?.scores || [];

  return (
    <div className="flex-1 max-w-7xl mx-auto w-full flex flex-col gap-gutter">
      {/* Header Actions */}
      <header className="flex items-center justify-between mb-sm">
        <Link to="/" className="flex items-center gap-2 text-primary hover:text-primary-container transition-colors">
          <span className="material-symbols-outlined text-xl">arrow_back</span>
          <span className="font-headline-md">Result Analysis</span>
        </Link>
        <div className="flex items-center gap-4">
          <button className="text-outline hover:text-on-surface transition-colors p-2 rounded-full hover:bg-surface-variant">
            <span className="material-symbols-outlined text-xl">share</span>
          </button>
          <button className="text-outline hover:text-on-surface transition-colors p-2 rounded-full hover:bg-surface-variant">
            <span className="material-symbols-outlined text-xl">download</span>
          </button>
        </div>
      </header>

      {/* Top Overview Card */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/30 p-gutter flex flex-col md:flex-row justify-between items-center gap-lg">
        <div className="flex-1 space-y-4">
          <div>
            <h1 className="font-headline-lg text-on-surface mb-1">Final Semester Exam</h1>
            <p className="font-body-md text-on-surface-variant">Class Rank: {result?.class_rank || 'N/A'}</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center gap-1 px-3 py-1 bg-tertiary-container/10 text-tertiary-container font-label-md rounded-full border border-tertiary-container/20">
              <span className="material-symbols-outlined" style={{ fontSize: '14px' }}>star</span>
              GPA {result?.gpa || '0.0'}
            </span>
            <span className={`inline-flex items-center gap-1 px-3 py-1 font-label-md rounded-full border ${result?.status === 'Pass' ? 'bg-emerald-100 text-emerald-800 border-emerald-200' : 'bg-red-100 text-red-800 border-red-200'}`}>
              <span className="material-symbols-outlined" style={{ fontSize: '14px' }}>
                {result?.status === 'Pass' ? 'check_circle' : 'cancel'}
              </span>
              {result?.status || 'N/A'}
            </span>
          </div>
        </div>
        <div className="relative w-32 h-32 flex items-center justify-center">
          <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
            <circle className="text-surface-variant" cx="50" cy="50" fill="none" r="45" stroke="currentColor" strokeWidth="8"></circle>
            <circle className="text-primary" cx="50" cy="50" fill="none" r="45" stroke="currentColor" strokeDasharray="282.7" strokeDashoffset={282.7 - (282.7 * (result?.total_score || 0) / 100)} strokeLinecap="round" strokeWidth="8"></circle>
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="font-headline-lg text-primary font-bold">{result?.total_score || 0}%</span>
            <span className="font-label-md text-on-surface-variant uppercase tracking-wider">Score</span>
          </div>
        </div>
      </div>

      {/* Merit Badges */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-md">
        <div className="bg-gradient-to-br from-[#4facfe] to-[#00f2fe] p-4 rounded-xl shadow-sm flex items-start gap-3 text-white">
          <span className="material-symbols-outlined text-2xl mt-1">auto_awesome</span>
          <p className="font-body-sm leading-relaxed">
            🌟 You are a superstar in Mathematics and Computer Sci!
          </p>
        </div>
        <div className="bg-gradient-to-br from-[#667eea] to-[#764ba2] p-4 rounded-xl shadow-sm flex items-start gap-3 text-white">
          <span className="material-symbols-outlined text-2xl mt-1">emoji_events</span>
          <p className="font-body-sm leading-relaxed">
            🏆 You are in the top 5! Keep up the momentum.
          </p>
        </div>
        <div className="bg-gradient-to-br from-[#38f9d7] to-[#43e97b] p-4 rounded-xl shadow-sm flex items-start gap-3 text-[#0f3a22]">
          <span className="material-symbols-outlined text-2xl mt-1">trending_up</span>
          <p className="font-body-sm leading-relaxed font-medium">
            📈 Your performance improved by 5% compared to the last exam.
          </p>
        </div>
      </div>

      {/* Marksheet Table */}
      <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/30 overflow-hidden flex flex-col">
        <div className="p-md border-b border-outline-variant/30">
          <h2 className="font-headline-md text-on-surface">Marksheet</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-surface-container-low border-b border-outline-variant/30">
                <th className="p-4 font-label-md text-on-surface-variant font-semibold">Subject</th>
                <th className="p-4 font-label-md text-on-surface-variant font-semibold">Marks</th>
                <th className="p-4 font-label-md text-on-surface-variant font-semibold">Grade</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/20">
              {scores.map((score: any) => (
                <tr key={score.id} className="hover:bg-surface-container-low/50 transition-colors">
                  <td className="p-4 font-body-sm text-on-surface">{score.subject_name}</td>
                  <td className="p-4 font-body-sm text-on-surface">{score.marks_obtained} / {score.total_marks}</td>
                  <td className="p-4 font-body-sm text-emerald-600 font-medium">{score.grade}</td>
                </tr>
              ))}
              {scores.length === 0 && (
                <tr>
                  <td colSpan={3} className="p-4 text-center text-on-surface-variant">No scores available.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
