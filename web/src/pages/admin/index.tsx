import { useState, useRef, useEffect, type DragEvent, type ChangeEvent } from 'react';
import { AdminLayout } from '../../components/layouts';
import { Card, DataTable, Icon, PageHeader } from '../../components/common/ui';
import { periods, useTimetable, weekdays, type SlotId } from '../../stores/timetableStore';
import { request } from '../../services/api/client';

interface DocumentItem {
  id?: string;
  filename: string;
  upload_date: string;
  status: string;
  extracted_data: any;
}
const Summary = ({ items }: { items: string[][] }) => <div className="stats">{items.map(([value, label, icon]) => <Card key={label}><Icon>{icon}</Icon><strong>{value}</strong><span>{label}</span></Card>)}</div>;

export function Exams() { return <AdminLayout><PageHeader title="Exam and Results Management" subtitle="Schedule examinations and monitor grading progress." /><Summary items={[['04', 'Upcoming exams', 'event'], ['82%', 'Average score', 'analytics'], ['68%', 'Grading progress', 'task_alt']]} /><Card><h2>Upcoming Examinations</h2><DataTable headers={['Subject', 'Date', 'Hall', 'Proctor', 'Status']} rows={[['Mathematics', 'Oct 24, 2024', 'Hall A', 'Mr. Davis', 'Scheduled'], ['Physics', 'Oct 26, 2024', 'Hall B', 'Mrs. Chen', 'Scheduled'], ['Chemistry', 'Oct 29, 2024', 'Lab 2', 'Ms. Lee', 'Draft']]} /></Card></AdminLayout>; }


export function Documents() {
  const API_URL = "http://localhost:8000/api/v1";

  const [isUploading, setIsUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");

  const [pendingFile, setPendingFile] = useState<File | null>(null);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [showCategoryModal, setShowCategoryModal] =
    useState(false);

  const [tableRows, setTableRows] = useState<any[][]>([]);
  const [isLoadingDocuments, setIsLoadingDocuments] =
    useState(true);

  const fileInputRef =
    useRef<HTMLInputElement>(null);

  const categories = [
    "Student Records",
    "Academic",
    "Finance",
    "Attendance",
    "Administrative",
    "Examination",
    "HR",
    "Other",
  ];

  // =========================================================
  // FETCH DOCUMENTS
  // =========================================================

  const fetchDocuments = async () => {
    try {
      setIsLoadingDocuments(true);

      const response = await fetch(
        `${API_URL}/documents`
      );

      if (!response.ok) {
        throw new Error(
          `HTTP ${response.status}`
        );
      }

      const data = await response.json();

      console.log(
        "DOCUMENTS FROM API:",
        data
      );

      /*
       * New backend returns:
       *
       * [
       *   {
       *     id,
       *     filename,
       *     path,
       *     category,
       *     status,
       *     upload_date,
       *     extracted_data
       *   }
       * ]
       */

      const documents = Array.isArray(data)
        ? data
        : Array.isArray(data.items)
        ? data.items
        : [];

      console.log(
        "DOCUMENT COUNT FROM API:",
        documents.length
      );

      const rows = documents.map(
        (doc: any) => {
          /*
           * This URL points to the NEW backend
           * endpoint which generates a clean
           * digitized PDF.
           */
          const digitizedDownloadUrl =
            `${API_URL}/documents/${doc.id}/download`;

          /*
           * Document name
           *
           * Clicking this downloads the digitized
           * PDF, NOT the original uploaded file.
           */
          const documentCell = (
            <a
              key={doc.id}
              href={digitizedDownloadUrl}
              download
              title="Download digitized document"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "7px",
                color: "#6750A4",
                fontWeight: 600,
                textDecoration: "none",
                cursor: "pointer",
              }}
            >
              <Icon>download</Icon>

              <span>
                {doc.filename ||
                  "Untitled Document"}
              </span>
            </a>
          );

          /*
           * Status formatting
           */
          let status = "Completed";

          if (doc.status) {
            status =
              doc.status
                .charAt(0)
                .toUpperCase() +
              doc.status.slice(1);
          }

          /*
           * Date formatting
           */
          let uploadDate = "Today";

          if (doc.upload_date) {
            uploadDate =
              new Date(
                doc.upload_date
              ).toLocaleDateString(
                "en-US",
                {
                  month: "short",
                  day: "numeric",
                  year: "numeric",
                }
              );
          }

          return [
            documentCell,

            /*
             * Category is now a database field:
             *
             * doc.category
             *
             * NOT:
             *
             * doc.extracted_data.category
             */
            doc.category || "Other",

            /*
             * requested_by is not currently part
             * of your Document model.
             */
            doc.extracted_data
              ?.requested_by ||
              "System User",

            uploadDate,

            status,
          ];
        }
      );

      setTableRows(rows);
    } catch (error) {
      console.error(
        "Failed to fetch documents:",
        error
      );

      setTableRows([]);

      setUploadMessage(
        "Unable to load documents."
      );
    } finally {
      setIsLoadingDocuments(false);
    }
  };

  // =========================================================
  // INITIAL LOAD
  // =========================================================

  useEffect(() => {
    fetchDocuments();
  }, []);

  // =========================================================
  // FILE SELECTED
  // =========================================================

  /*
   * IMPORTANT:
   *
   * Selecting a file does NOT upload it immediately.
   *
   * We first ask the user for the category.
   */
  const selectFileForUpload = (
    file: File
  ) => {
    console.log(
      "FILE SELECTED:",
      file.name
    );

    setPendingFile(file);
    setSelectedCategory("");
    setUploadMessage("");
    setShowCategoryModal(true);
  };

  // =========================================================
  // FILE PICKER
  // =========================================================

  const onFileChange = (
    e: ChangeEvent<HTMLInputElement>
  ) => {
    const file = e.target.files?.[0];

    if (!file) {
      return;
    }

    selectFileForUpload(file);

    /*
     * Reset input so the same file can be
     * selected again later.
     */
    e.target.value = "";
  };

  // =========================================================
  // DRAG & DROP
  // =========================================================

  const onDrop = (
    e: DragEvent<HTMLDivElement>
  ) => {
    e.preventDefault();

    const file =
      e.dataTransfer.files?.[0];

    if (!file) {
      return;
    }

    selectFileForUpload(file);
  };

  const onDragOver = (
    e: DragEvent<HTMLDivElement>
  ) => {
    e.preventDefault();
  };

  // =========================================================
  // ACTUAL UPLOAD
  // =========================================================

  const handleFileUpload = async (
    file: File,
    category: string
  ) => {
    setIsUploading(true);

    setUploadMessage(
      "Uploading file and running OCR..."
    );

    const formData = new FormData();

    /*
     * Backend expects:
     *
     * file
     * category
     */
    formData.append(
      "file",
      file
    );

    formData.append(
      "category",
      category
    );

    try {
      console.log(
        "UPLOADING:",
        {
          filename: file.name,
          category,
        }
      );

      const response = await fetch(
        `${API_URL}/documents/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data =
        await response.json();

      console.log(
        "UPLOAD RESPONSE:",
        data
      );

      if (!response.ok) {
        throw new Error(
          data.detail ||
            `Upload failed: ${response.status}`
        );
      }

      setUploadMessage(
        `Success! ${
          data.filename ||
          file.name
        } has been digitized and saved.`
      );

      /*
       * Close category dialog.
       */
      setShowCategoryModal(false);

      setPendingFile(null);
      setSelectedCategory("");

      /*
       * Refresh table from PostgreSQL.
       */
      await fetchDocuments();
    } catch (error) {
      console.error(
        "Upload failed:",
        error
      );

      setUploadMessage(
        error instanceof Error
          ? error.message
          : "Error uploading document."
      );
    } finally {
      setIsUploading(false);
    }
  };

  // =========================================================
  // CONFIRM CATEGORY
  // =========================================================

  const confirmCategory = async () => {
    if (!pendingFile) {
      return;
    }

    if (!selectedCategory) {
      setUploadMessage(
        "Please select a document category."
      );

      return;
    }

    await handleFileUpload(
      pendingFile,
      selectedCategory
    );
  };

  // =========================================================
  // CANCEL CATEGORY
  // =========================================================

  const cancelCategorySelection = () => {
    if (isUploading) {
      return;
    }

    setPendingFile(null);
    setSelectedCategory("");
    setShowCategoryModal(false);
    setUploadMessage("");
  };

  // =========================================================
  // RENDER
  // =========================================================

  return (
    <AdminLayout>
      <PageHeader
        title="Administrative Paperwork Manager"
        subtitle="Manage document requests from one place."
      />

      {/* =====================================================
          UPLOAD CARD
          ===================================================== */}

      <Card
        className="dropzone"
        onDrop={onDrop}
        onDragOver={onDragOver}
      >
        <Icon>
          cloud_upload
        </Icon>

        <h2>
          Upload a document
        </h2>

        <p>
          Drag and drop files here, or browse
          from your device
        </p>

        <input
          type="file"
          ref={fileInputRef}
          style={{
            display: "none",
          }}
          onChange={onFileChange}
          accept=".pdf,.jpg,.jpeg,.png"
        />

        <button
          className="primary-btn"
          onClick={() =>
            fileInputRef.current?.click()
          }
          disabled={isUploading}
        >
          {isUploading
            ? "Processing..."
            : "Choose file"}
        </button>

        {uploadMessage && (
          <p
            style={{
              marginTop: "12px",
            }}
          >
            {uploadMessage}
          </p>
        )}
      </Card>

      {/* =====================================================
          DOCUMENT TABLE
          ===================================================== */}

      <Card>
        <h2>
          Digitized Documents
        </h2>

        {isLoadingDocuments ? (
          <p>
            Loading documents...
          </p>
        ) : (
          <DataTable
            headers={[
              "Digitized Document",
              "Category",
              "Requested by",
              "Date",
              "Status",
            ]}
            rows={tableRows}
          />
        )}
      </Card>

      {/* =====================================================
          CATEGORY MODAL
          ===================================================== */}

      {showCategoryModal && (
        <div
          onClick={
            cancelCategorySelection
          }
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 9999,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background:
              "rgba(0, 0, 0, 0.45)",
            padding: "20px",
          }}
        >
          <div
            onClick={(e) =>
              e.stopPropagation()
            }
            style={{
              width: "100%",
              maxWidth: "500px",
              background: "#ffffff",
              borderRadius: "16px",
              padding: "28px",
              boxShadow:
                "0 20px 60px rgba(0, 0, 0, 0.25)",
            }}
          >
            {/* Modal header */}

            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent:
                  "space-between",
                marginBottom: "8px",
              }}
            >
              <h2
                style={{
                  margin: 0,
                }}
              >
                Select Document Category
              </h2>

              <button
                type="button"
                onClick={
                  cancelCategorySelection
                }
                disabled={isUploading}
                style={{
                  border: "none",
                  background:
                    "transparent",
                  cursor: "pointer",
                  fontSize: "24px",
                  lineHeight: 1,
                }}
              >
                ×
              </button>
            </div>

            <p
              style={{
                color: "#666",
                marginTop: "8px",
                marginBottom:
                  "20px",
              }}
            >
              Select a category before
              the document is processed.
            </p>

            {/* Selected file */}

            {pendingFile && (
              <div
                style={{
                  display: "flex",
                  alignItems:
                    "center",
                  gap: "10px",
                  padding:
                    "12px 14px",
                  marginBottom:
                    "20px",
                  borderRadius:
                    "10px",
                  background:
                    "#f5f3fa",
                }}
              >
                <Icon>
                  description
                </Icon>

                <div
                  style={{
                    overflow: "hidden",
                  }}
                >
                  <div
                    style={{
                      fontSize:
                        "12px",
                      color:
                        "#777",
                      marginBottom:
                        "3px",
                    }}
                  >
                    Selected file
                  </div>

                  <div
                    style={{
                      fontWeight:
                        600,
                      overflow:
                        "hidden",
                      textOverflow:
                        "ellipsis",
                      whiteSpace:
                        "nowrap",
                    }}
                  >
                    {
                      pendingFile.name
                    }
                  </div>
                </div>
              </div>
            )}

            {/* Category */}

            <label
              htmlFor="document-category"
              style={{
                display: "block",
                fontWeight: 600,
                marginBottom: "8px",
              }}
            >
              Category
            </label>

            <select
              id="document-category"
              value={
                selectedCategory
              }
              onChange={(e) =>
                setSelectedCategory(
                  e.target.value
                )
              }
              disabled={isUploading}
              style={{
                width: "100%",
                boxSizing:
                  "border-box",
                padding:
                  "12px 14px",
                borderRadius:
                  "8px",
                border:
                  "1px solid #ccc",
                background:
                  "#fff",
                fontSize:
                  "15px",
                outline:
                  "none",
                marginBottom:
                  "24px",
              }}
            >
              <option value="">
                Select category
              </option>

              {categories.map(
                (category) => (
                  <option
                    key={category}
                    value={category}
                  >
                    {category}
                  </option>
                )
              )}
            </select>

            {/* Actions */}

            <div
              style={{
                display: "flex",
                justifyContent:
                  "flex-end",
                gap: "10px",
              }}
            >
              <button
                type="button"
                onClick={
                  cancelCategorySelection
                }
                disabled={isUploading}
                style={{
                  padding:
                    "10px 18px",
                  borderRadius:
                    "8px",
                  border:
                    "1px solid #ccc",
                  background:
                    "#fff",
                  cursor:
                    "pointer",
                }}
              >
                Cancel
              </button>

              <button
                type="button"
                className="primary-btn"
                onClick={
                  confirmCategory
                }
                disabled={
                  !selectedCategory ||
                  isUploading
                }
              >
                {isUploading
                  ? "Processing..."
                  : "Continue & Process"}
              </button>
            </div>
          </div>
        </div>
      )}
    </AdminLayout>
  );
}
export function Activities() { const clubs = ['Debate Club', 'Soccer Match: Varsity vs. Oakwood', 'Art Exhibition Setup', 'Premiers Club']; return <AdminLayout><PageHeader title="Student Activities Dashboard" subtitle="Monitor events, clubs, and student engagement." /><div className="activity-grid"><div><h2>Upcoming Events & Clubs</h2><div className="club-grid">{clubs.map((club, i) => <Card key={club}><div className="club-icon"><Icon>celebration</Icon></div><h3>{club}</h3><p>Next: <b>Oct {27 + i}</b></p><p>Supervisor: <b>Mrs. Chen</b></p><p>Enrollment: <b>{45 - i * 5}/50</b></p></Card>)}</div></div><Card><h2>Recent Activity Feed</h2><div className="feed">{['Science Club submitted project report', 'New Chess Club members registered', 'Basketball practice scheduled'].map(activity => <div key={activity}><i className="current" /><p>{activity}<small>Today, 10:30 AM</small></p></div>)}</div></Card></div></AdminLayout>; }

const teacherPermissionCatalog = [{ key: 'manage_students', label: 'Manage Students' }, { key: 'manage_exams', label: 'Manage Exams' }, { key: 'enter_results', label: 'Enter Results' }, { key: 'manage_timetable', label: 'Manage Timetable' }, { key: 'manage_assignments', label: 'Manage Assignments' }, { key: 'manage_documents', label: 'Manage Documents' }, { key: 'manage_activities', label: 'Manage Activities' }];
export function TeacherManagement() { const [teachers, setTeachers] = useState<{ name: string; email: string; permissions: string[] }[]>(() => { try { return JSON.parse(localStorage.getItem('edusync-teachers') || '[]'); } catch { return []; } }); const [name, setName] = useState(''); const [email, setEmail] = useState(''); const [password, setPassword] = useState('Teacher@123'); const [permissions, setPermissions] = useState<string[]>(['manage_assignments', 'manage_exams']); const toggle = (key: string) => setPermissions(current => current.includes(key) ? current.filter(item => item !== key) : [...current, key]); const create = (event: React.FormEvent) => { event.preventDefault(); const next = [...teachers, { name, email, permissions }]; setTeachers(next); localStorage.setItem('edusync-teachers', JSON.stringify(next)); setName(''); setEmail(''); setPassword('Teacher@123'); }; return <AdminLayout><PageHeader title="Manage Teachers" subtitle="Create teacher credentials and assign explicit permissions." action="" /><div className="teacher-management-grid"><Card><div className="card-title"><h2>Create Teacher Credential</h2><Icon>person_add</Icon></div><form className="teacher-form" onSubmit={create}><label>Full name<input required value={name} onChange={event => setName(event.target.value)} placeholder="e.g. Mrs. Chen" /></label><label>Email<input required type="email" value={email} onChange={event => setEmail(event.target.value)} placeholder="teacher@edusync.local" /></label><label>Temporary password<input required minLength={8} value={password} onChange={event => setPassword(event.target.value)} /></label><fieldset><legend>Permissions</legend>{teacherPermissionCatalog.map(permission => <label className="permission-row" key={permission.key}><input type="checkbox" checked={permissions.includes(permission.key)} onChange={() => toggle(permission.key)} /><span><b>{permission.label}</b><small>{permission.key}</small></span></label>)}</fieldset><button className="primary-btn" type="submit"><Icon>person_add</Icon>Create teacher</button></form></Card><Card><div className="card-title"><h2>Teacher Accounts</h2><span className="muted">{teachers.length} created locally</span></div>{teachers.length === 0 ? <div className="empty-state"><Icon>group</Icon><p>No additional teachers created yet.</p></div> : teachers.map(teacher => <div className="teacher-row" key={teacher.email}><div className="avatar">{teacher.name.slice(0, 2).toUpperCase()}</div><div><b>{teacher.name}</b><small>{teacher.email}</small><p>{teacher.permissions.length} permissions granted</p></div></div>)}</Card></div></AdminLayout>; }

export function Timetable() {
  const { state, assign, clear, setClass, save, generate } = useTimetable();
  const [isDragging, setIsDragging] = useState(false);
  const [dragTarget, setDragTarget] = useState<SlotId | null>(null);
  const [selectedSubjectId, setSelectedSubjectId] = useState<string | null>(null);
  const onDrop = (event: DragEvent<HTMLDivElement>, slotId: SlotId) => { event.preventDefault(); const subjectId = event.dataTransfer.getData('application/x-edusync-subject') || event.dataTransfer.getData('text/plain') || selectedSubjectId; if (subjectId) assign(slotId, subjectId); setIsDragging(false); setDragTarget(null); };
  const grades = [...new Set(state.classes.map(item => item.grade))];
  const sections = [...new Set(state.classes.filter(item => item.grade === state.grade).map(item => item.section))];
  return <AdminLayout><PageHeader title="Drag and Drop Timetable Builder" subtitle="Review the recommended weekly plan, then make any adjustments." /><div className="timetable-toolbar"><label>Grade<select value={state.grade} onChange={event => setClass(event.target.value, state.classes.find(item => item.grade === event.target.value)?.section || 'A')}>{(grades.length ? grades : ['10', '11', '12']).map(grade => <option key={grade}>{grade}</option>)}</select></label><label>Section<select value={state.section} onChange={event => setClass(state.grade, event.target.value)}>{(sections.length ? sections : ['A', 'B', 'C']).map(section => <option key={section}>{section}</option>)}</select></label><span className="sync-state">{state.loading ? 'Loading recommendation…' : state.saving ? 'Saving…' : state.dirty ? 'Unsaved changes' : state.lastSavedAt ? 'All changes saved' : 'Recommended plan ready'}</span><button className="outline-btn timetable-generate" disabled={state.loading || state.saving} onClick={() => void generate()}><Icon>auto_awesome</Icon>Generate plan</button><button className="primary-btn" disabled={!state.dirty || state.saving} onClick={() => void save()}><Icon>save</Icon>{state.saving ? 'Saving' : 'Save timetable'}</button></div>{state.error && <p className="timetable-message error"><Icon>error</Icon>{state.error}</p>}{state.warnings.map(warning => <p className="timetable-message" key={warning}><Icon>info</Icon>{warning}</p>)}<div className="timetable-layout"><Card><h2>Subjects & Workload</h2>{state.subjects.map((subject, i) => <div className={`palette-item ${selectedSubjectId === subject.id ? 'selected' : ''}`} draggable onClick={() => setSelectedSubjectId(subject.id)} onDragStart={event => { event.dataTransfer.effectAllowed = 'copy'; event.dataTransfer.setData('application/x-edusync-subject', subject.id); event.dataTransfer.setData('text/plain', subject.id); setSelectedSubjectId(subject.id); setIsDragging(true); }} onDragEnd={() => { setIsDragging(false); setDragTarget(null); }} key={subject.id} title={`${subject.teacher} · ${subject.weekly_periods} periods/week`}><span className={`swatch s${i}`} /><span>{subject.name}<small>{subject.weekly_periods} periods/week</small></span><Icon>drag_indicator</Icon></div>)}</Card><Card className="timetable"><h2>Grade {state.grade} • Section {state.section}</h2><div className="schedule-grid"><b>Time</b>{weekdays.map(day => <b key={day}>{day}</b>)}{periods.map(time => <><span className="time" key={time}>{time}</span>{weekdays.map(day => { const id = `${day}-${time}` as SlotId; const slot = state.slots.find(item => item.id === id); const classes = `slot ${slot?.subject ? 'filled' : ''} ${isDragging ? 'dragging' : ''} ${dragTarget === id ? 'drag-target' : ''}`; return <div className={classes} key={id} title={slot?.teacher || ''} onClick={() => selectedSubjectId && assign(id, selectedSubjectId)} onDragEnter={() => setDragTarget(id)} onDragOver={event => { event.preventDefault(); event.dataTransfer.dropEffect = 'copy'; }} onDragLeave={() => setDragTarget(null)} onDrop={event => onDrop(event, id)} onDoubleClick={() => slot?.subject && clear(id)}>{slot?.subject || 'Drop subject'}</div>; })}</>)}</div><p className="timetable-help"><Icon>info</Icon>Drag a subject into a slot, or select a subject and click a slot. Double-click a filled slot to clear it, then save your changes.</p></Card></div></AdminLayout>;
}

type SetupClass = { grade: string; section: string };
type SetupTeacher = { id: string; name: string; email: string };
type SetupSubject = { id: string; name: string; teacher_id: string; teacher: string; weekly_periods: number };
export function TimetableSettings() {
  const [classes, setClasses] = useState<SetupClass[]>([]); const [teachers, setTeachers] = useState<SetupTeacher[]>([]); const [selected, setSelected] = useState<SetupClass>({ grade: '12', section: 'A' }); const [subjects, setSubjects] = useState<SetupSubject[]>([]); const [grade, setGrade] = useState('Grade 9'); const [section, setSection] = useState('A'); const [subjectName, setSubjectName] = useState(''); const [teacherId, setTeacherId] = useState(''); const [weeklyPeriods, setWeeklyPeriods] = useState(3); const [message, setMessage] = useState('');
  const loadClasses = async () => { const rows = await request<SetupClass[]>('/timetable/classes'); setClasses(rows); return rows; };
  const loadConfiguration = async (next = selected) => { const result = await request<{ subjects: SetupSubject[] }>(`/timetable/configuration?grade=${encodeURIComponent(next.grade)}&section=${encodeURIComponent(next.section)}`); setSubjects(result.subjects); };
  useEffect(() => { void Promise.all([loadClasses(), request<SetupTeacher[]>('/timetable/teachers').then(setTeachers)]).then(() => loadConfiguration()).catch(() => setMessage('Sign in as an administrator to manage timetable setup.')); }, []);
  const chooseClass = (value: string) => { const [nextGrade, nextSection] = value.split('|'); const next = { grade: nextGrade, section: nextSection }; setSelected(next); void loadConfiguration(next).catch(() => setMessage('Could not load this class configuration.')); };
  const addClass = async (event: React.FormEvent) => { event.preventDefault(); try { const next = await request<SetupClass>('/timetable/classes', { method: 'POST', body: JSON.stringify({ grade, section }) }); setMessage(`${next.grade} • ${next.section} was added.`); await loadClasses(); setSelected(next); await loadConfiguration(next); } catch { setMessage('Could not add the grade/section. It may already exist.'); } };
  const addSubject = async (event: React.FormEvent) => { event.preventDefault(); try { await request('/timetable/configuration/subjects?grade=' + encodeURIComponent(selected.grade) + '&section=' + encodeURIComponent(selected.section), { method: 'POST', body: JSON.stringify({ name: subjectName, teacher_id: teacherId, weekly_periods: weeklyPeriods }) }); setSubjectName(''); setMessage('Subject and weekly workload saved. Generate a new plan to apply it.'); await loadConfiguration(); } catch { setMessage('Could not save the subject. Select an active teacher and a unique subject name.'); } };
  const removeSubject = async (subject: SetupSubject) => { if (!window.confirm(`Delete ${subject.name}? Any timetable periods using it will also be removed.`)) return; try { await request(`/timetable/configuration/subjects/${subject.id}`, { method: 'DELETE' }); setMessage(`${subject.name} was deleted from this class.`); await loadConfiguration(); } catch { setMessage(`Could not delete ${subject.name}.`); } };
  const deleteClass = async () => { const configuration = await request<{ class_id: string }>('/timetable/configuration?grade=' + encodeURIComponent(selected.grade) + '&section=' + encodeURIComponent(selected.section)); if (!window.confirm(`Delete Grade ${selected.grade} • Section ${selected.section}? Remove all subjects first.`)) return; try { await request(`/timetable/classes/${configuration.class_id}`, { method: 'DELETE' }); setMessage('Grade/section deleted.'); const rows = await loadClasses(); const next = rows[0] || { grade: '12', section: 'A' }; setSelected(next); if (rows.length) await loadConfiguration(next); else setSubjects([]); } catch { setMessage('This grade/section still has subjects. Delete them first, then remove the class.'); } };
  return <AdminLayout><PageHeader title="Timetable Setup" subtitle="Manage grade sections, subjects, workloads, and teaching assignments." /><p className="setup-message">{message || 'These settings are used by the timetable recommendation engine.'}</p><div className="setup-grid"><Card><h2>Add grade & section</h2><form className="setup-form" onSubmit={addClass}><label>Grade<input value={grade} onChange={event => setGrade(event.target.value)} placeholder="e.g. Grade 9" required /></label><label>Section<input value={section} onChange={event => setSection(event.target.value)} placeholder="e.g. A" required /></label><button className="primary-btn" type="submit"><Icon>add</Icon>Add class</button></form></Card><Card><h2>Class configuration</h2><label className="setup-field">Grade & section<select value={`${selected.grade}|${selected.section}`} onChange={event => chooseClass(event.target.value)}>{classes.map(item => <option key={`${item.grade}|${item.section}`} value={`${item.grade}|${item.section}`}>Grade {item.grade} • Section {item.section}</option>)}</select></label><button className="text-btn danger-btn" onClick={() => void deleteClass()}><Icon>delete</Icon>Delete this grade & section</button></Card></div><div className="setup-grid"><Card><h2>Add subject & workload</h2><form className="setup-form" onSubmit={addSubject}><label>Subject name<input value={subjectName} onChange={event => setSubjectName(event.target.value)} placeholder="e.g. Biology" required /></label><label>Assigned teacher<select value={teacherId} onChange={event => setTeacherId(event.target.value)} required><option value="" disabled>Select teacher</option>{teachers.map(teacher => <option value={teacher.id} key={teacher.id}>{teacher.name}</option>)}</select></label><label>Periods per week<input type="number" min="1" max="20" value={weeklyPeriods} onChange={event => setWeeklyPeriods(Number(event.target.value))} required /></label><button className="primary-btn" type="submit"><Icon>add</Icon>Add subject</button></form></Card><Card><div className="card-title"><h2>Subjects for Grade {selected.grade} • {selected.section}</h2><span className="muted">{subjects.reduce((total, subject) => total + subject.weekly_periods, 0)} periods/week</span></div>{subjects.length ? subjects.map(subject => <div className="setup-subject" key={subject.id}><div><b>{subject.name}</b><small>{subject.teacher} · {subject.weekly_periods} periods/week</small></div><button className="icon-btn" title={`Delete ${subject.name}`} onClick={() => void removeSubject(subject)}><Icon>delete</Icon></button></div>) : <div className="empty-state"><Icon>menu_book</Icon><p>No subjects configured for this class.</p></div>}</Card></div></AdminLayout>;
}
