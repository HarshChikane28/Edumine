import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import StudentShell from './app/StudentShell';
import AdminShell from './app/AdminShell';

// Pages
import Dashboard from './pages/student/Dashboard';
import Assignments from './pages/student/Assignments';
import Profile from './pages/student/Profile';
import Results from './pages/student/Results';

import Exams from './pages/admin/Exams';
import Documents from './pages/admin/Documents';
import Activities from './pages/admin/Activities';
import Timetable from './pages/admin/Timetable';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Student Routes */}
          <Route path="/" element={<StudentShell />}>
            <Route index element={<Dashboard />} />
            <Route path="assignments" element={<Assignments />} />
            <Route path="profile" element={<Profile />} />
            <Route path="results/:examId" element={<Results />} />
          </Route>

          {/* Admin Routes */}
          <Route path="/admin" element={<AdminShell />}>
            <Route index element={<Navigate to="/admin/exams" replace />} />
            <Route path="exams" element={<Exams />} />
            <Route path="documents" element={<Documents />} />
            <Route path="activities" element={<Activities />} />
            <Route path="timetable" element={<Timetable />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
