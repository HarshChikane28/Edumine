import { useQuery } from '@tanstack/react-query';
import api from './client';

export const useStudentDashboard = (studentId: number) => {
  return useQuery({
    queryKey: ['dashboard', studentId],
    queryFn: async () => {
      const { data } = await api.get(`/students/${studentId}/dashboard`);
      return data;
    },
    enabled: !!studentId
  });
};

export const useStudentAssignments = (studentId: number, status?: string) => {
  return useQuery({
    queryKey: ['assignments', studentId, status],
    queryFn: async () => {
      const url = status ? `/students/${studentId}/assignments?status=${status}` : `/students/${studentId}/assignments`;
      const { data } = await api.get(url);
      return data;
    },
    enabled: !!studentId
  });
};

export const useStudentProfile = (studentId: number) => {
  return useQuery({
    queryKey: ['profile', studentId],
    queryFn: async () => {
      const { data } = await api.get(`/students/${studentId}/profile`);
      return data;
    },
    enabled: !!studentId
  });
};

export const useStudentResults = (studentId: number, examId?: number) => {
  return useQuery({
    queryKey: ['results', studentId, examId],
    queryFn: async () => {
      const url = examId ? `/students/${studentId}/results?exam_id=${examId}` : `/students/${studentId}/results`;
      const { data } = await api.get(url);
      return data;
    },
    enabled: !!studentId
  });
};
