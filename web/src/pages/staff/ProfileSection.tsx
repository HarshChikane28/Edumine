import { useEffect, useState } from 'react';
import { AdminLayout } from '../../components/layouts';
import { Card, Icon, PageHeader } from '../../components/common/ui';
import { getStoredRole } from '../../app/App';
import { request } from '../../services/api/client';
import '../../styles/profile.css';

type Profile = { role: string; personal: Record<string, any>; professional: Record<string, any> };
type Doc = { type: string; label: string; required: boolean; status: string; filename?: string; uploaded_at?: string };
const personalFields = ['first_name','middle_name','last_name','date_of_birth','gender','blood_group','marital_status','nationality','mother_tongue','personal_email','alternate_mobile','emergency_contact_name','emergency_contact_number','emergency_contact_relationship','birth_place','birth_country','birth_state','birth_district','native_place','native_country','native_state','native_district'];
const professionalFields = ['employee_id','employee_code','department','designation','class_grade_assigned','joining_date','employment_type','employment_status','qualification','highest_qualification','specialization','university_college','graduation_year','teaching_experience','previous_organization','previous_designation','work_experience','reporting_manager','branch_campus','staff_type'];
const title = (value: string) => value.replace(/_/g, ' ').replace(/\b\w/g, letter => letter.toUpperCase());

export default function StaffProfile() {
  const role = getStoredRole();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [documents, setDocuments] = useState<Doc[]>([]);
  const [form, setForm] = useState<Record<string, any>>({});
  const [selected, setSelected] = useState('');
  const [editing, setEditing] = useState(false);
  const [activeTab, setActiveTab] = useState<'personal' | 'professional' | 'documents'>('personal');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const load = async () => {
    try {
      const [data, docs] = await Promise.all([request<Profile>('/profiles/me'), request<Doc[]>('/profiles/me/documents')]);
      setProfile(data);
      setDocuments(docs);
      setForm({ ...data.personal, ...data.professional });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load profile.');
    }
  };

  useEffect(() => { void load(); }, []);

  const save = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      const data = await request<Profile>('/profiles/me', { method: 'PATCH', body: JSON.stringify(form) });
      setProfile(data);
      setEditing(false);
      setMessage('Profile details saved.');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to save profile.');
    }
  };

  const upload = async (type: string, file?: File) => {
    if (!file) return;
    const body = new FormData();
    body.append('file', file);
    try {
      await request(`/profiles/me/documents/${type}`, { method: 'POST', body });
      setSelected('');
      await load();
      setMessage('Document uploaded.');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to upload document.');
    }
  };

  const view = async (type: string) => {
    const response = await fetch(`/api/v1/profiles/me/documents/${type}/view`, { headers: { Authorization: `Bearer ${localStorage.getItem('edusync-token') || ''}` } });
    if (!response.ok) {
      setError('Unable to open document.');
      return;
    }
    window.open(URL.createObjectURL(await response.blob()), '_blank', 'noopener,noreferrer');
  };

  if (!profile) return <AdminLayout><div className="empty-state">{error || 'Loading profile…'}</div></AdminLayout>;

  const pending = documents.filter(doc => doc.status !== 'uploaded');
  const uploaded = documents.filter(doc => doc.status === 'uploaded');
  const initials = profile.personal.full_name?.split(' ').map((part: string) => part[0]).slice(0, 2).join('').toUpperCase() || (role === 'admin' ? 'AD' : 'TR');
  const fields = (section: 'personal' | 'professional', names: string[]) => <div className="detail-grid">{names.map(field => <span key={field}>{title(field)}<strong>{profile[section][field] || '—'}</strong></span>)}</div>;
  const inputs = (names: string[]) => names.map(field => <label key={field}>{title(field)}<input type={field.includes('date') ? 'date' : field.includes('year') ? 'number' : 'text'} value={form[field] || ''} onChange={event => setForm({ ...form, [field]: event.target.value })} /></label>);

  const personalSection = <Card className="profile-section-card"><div className="section-heading"><div><h2>Personal Details</h2><p className="muted">Basic identity and contact information.</p></div><Icon>person</Icon></div>{editing ? <form className="profile-form" onSubmit={save}><label>Full name<input value={form.full_name || ''} onChange={event => setForm({ ...form, full_name: event.target.value })} /></label><label>Official email<input type="email" value={form.official_email || ''} onChange={event => setForm({ ...form, official_email: event.target.value })} /></label>{inputs(personalFields)}<button className="primary-btn">Save personal details</button></form> : fields('personal', ['full_name', ...personalFields])}</Card>;
  const professionalSection = <Card className="profile-section-card"><div className="section-heading"><div><h2>Professional Details</h2><p className="muted">Employment, qualification and teaching information.</p></div><Icon>work</Icon></div>{editing ? <form className="profile-form" onSubmit={save}>{inputs(professionalFields)}<button className="primary-btn">Save professional details</button></form> : fields('professional', professionalFields)}</Card>;
  const documentsSection = <Card className="profile-section-card"><div className="section-heading"><div><h2>Upload Documents</h2><p className="muted">Select a pending document or replace an uploaded one below.</p></div><Icon>folder</Icon></div><div className="document-upload-picker"><select value={selected} onChange={event => setSelected(event.target.value)}><option value="">Select document to upload</option>{pending.map(doc => <option key={doc.type} value={doc.type}>{doc.label}</option>)}</select>{selected ? <label className="primary-btn upload-label"><Icon>upload</Icon>Choose file<input type="file" accept="application/pdf,image/png,image/jpeg" onChange={event => { void upload(selected, event.target.files?.[0]); event.currentTarget.value = ''; }} /></label> : <span className="muted">Choose a document type first</span>}</div><h3 className="document-subheading">Uploaded Documents</h3><div className="document-list">{uploaded.map(doc => <div className="document-row" key={doc.type}><div className="document-icon"><Icon>description</Icon></div><div className="document-info"><strong>{doc.label}</strong><span>{doc.filename}{doc.uploaded_at ? ` · ${new Date(doc.uploaded_at).toLocaleDateString()}` : ''}</span></div><button className="text-btn" onClick={() => void view(doc.type)}><Icon>visibility</Icon>View</button><label className="text-btn replace-document">Replace<input type="file" accept="application/pdf,image/png,image/jpeg" onChange={event => { void upload(doc.type, event.target.files?.[0]); event.currentTarget.value = ''; }} /></label></div>)}{uploaded.length === 0 && <div className="empty-state compact"><Icon>info</Icon>No documents uploaded yet.</div>}</div></Card>;
  const tabContent = activeTab === 'personal' ? personalSection : activeTab === 'professional' ? professionalSection : documentsSection;

  return <AdminLayout><PageHeader title={`${role === 'admin' ? 'Admin' : 'Teacher'} Profile`} subtitle="Your personal, professional and document information." />{message && <p className="profile-message"><Icon>check_circle</Icon>{message}</p>}{error && <p className="profile-error"><Icon>error</Icon>{error}</p>}<Card className="profile-hero"><div className="profile-avatar">{initials}</div><div><h1>{profile.personal.full_name}</h1><p>{role === 'admin' ? 'Administrator' : profile.professional.designation || 'Teacher'}</p><span className="muted">{profile.personal.official_email}</span></div><button className="outline-btn" onClick={() => setEditing(value => !value)}><Icon>edit</Icon>{editing ? 'Cancel' : 'Edit details'}</button></Card><nav className="profile-tabs" aria-label="Profile sections">{([['personal','Personal Details','person'],['professional','Professional Details','work'],['documents','Upload Documents','folder']] as const).map(([tab, name, icon]) => <button key={tab} className={activeTab === tab ? 'active' : ''} onClick={() => { setActiveTab(tab); setEditing(false); }}><Icon>{icon}</Icon><span>{name}</span></button>)}</nav>{tabContent}</AdminLayout>;
}
