import type { HTMLAttributes, ReactNode } from 'react';

export const Icon = ({ children }: { children: string }) => <span className="material-symbols-outlined">{children}</span>;
export const Card = ({ children, className = '', ...props }: HTMLAttributes<HTMLDivElement> & { children: ReactNode }) => <div className={`card ${className}`} {...props}>{children}</div>;
export const Status = ({ children }: { children: string }) => <span className={`status ${children.toLowerCase()}`}>{children}</span>;
export function PageHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: string }) { return <div className="page-heading"><div><h1>{title}</h1>{subtitle && <p>{subtitle}</p>}</div>{action && <button className="primary-btn"><Icon>add</Icon>{action}</button>}</div>; }
export function DataTable({ headers, rows }: { headers: string[]; rows: string[][] }) { return <div className="table-wrap"><table><thead><tr>{headers.map(h => <th key={h}>{h}</th>)}</tr></thead><tbody>{rows.map((row, i) => <tr key={i}>{row.map((value, j) => <td key={j}>{j === row.length - 1 ? <Status>{value}</Status> : value}</td>)}</tr>)}</tbody></table></div>; }
export const studentNavigation = [['dashboard', 'Home', 'home'], ['schedule', 'Timetable', 'calendar_month'], ['attendance', 'Attendance', 'fact_check'], ['assignments', 'Tasks', 'task_alt'], ['profile', 'Profile', 'person']] as const;
export const adminNavigation = [['exams', 'Exams', 'quiz'], ['documents', 'Paperwork', 'description'], ['activities', 'Activities', 'celebration'], ['admin-attendance', 'Attendance', 'fact_check'], ['timetable', 'Timetable', 'calendar_month'], ['timetable-settings', 'Timetable setup', 'tune']] as const;
