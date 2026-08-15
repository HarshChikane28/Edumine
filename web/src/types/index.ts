export type UserRole = 'student' | 'teacher' | 'admin';
export type AssignmentStatus = 'Pending' | 'Submitted' | 'Graded';
export type RequestStatus = 'Pending' | 'Processing' | 'Completed';

export interface Assignment { title: string; subject: string; due: string; status: AssignmentStatus; }
export interface ApiError { message: string; status?: number; }
