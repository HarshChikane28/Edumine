import { useState } from 'react';

export default function Timetable() {
  const timeSlots = [
    '8:00 AM', '9:00 AM', '10:00 AM', '11:00 AM', '12:00 PM', '1:00 PM'
  ];

  // A very basic mock schedule grid mapping [timeIndex][dayIndex] -> class object or null
  const schedule = [
    [null, { subject: 'Math', room: '101' }, { subject: 'Math', room: '101' }, null, null],
    [null, null, null, { subject: 'Science', room: '203' }, null],
    [null, { subject: 'Science', room: '203' }, null, { subject: 'English', room: '102' }, null],
    [{ subject: 'English', room: '102' }, null, { subject: 'English', room: '102' }, { subject: 'History', room: '105' }, null],
    [null, { subject: 'Science', room: '203' }, null, null, { subject: 'History', room: '105' }],
    [null, null, null, null, null]
  ];

  const subjects = ['Math', 'Science', 'English', 'History', 'Art', 'PE', 'Music', 'Biology'];
  const rooms = ['Room 101', 'Room 102', 'Room 203', 'Room 301', 'Gym', 'Lab A'];

  return (
    <div className="flex flex-col h-[calc(100vh-6rem)] gap-gutter">
      
      {/* Header and Filters */}
      <div className="flex gap-4 items-center bg-surface-container-lowest p-4 rounded-xl border border-outline-variant shadow-sm shrink-0">
        <h2 className="font-headline-lg text-primary mr-auto">Timetable Builder</h2>
        <div className="flex items-center gap-2">
          <label className="font-label-md text-on-surface-variant">Grade:</label>
          <select className="form-select bg-surface border border-outline-variant rounded-lg text-body-sm py-1.5 pl-3 pr-8 focus:ring-primary focus:border-primary">
            <option>Grade 10</option>
          </select>
        </div>
        <div className="flex items-center gap-2">
          <label className="font-label-md text-on-surface-variant">Section:</label>
          <select className="form-select bg-surface border border-outline-variant rounded-lg text-body-sm py-1.5 pl-3 pr-8 focus:ring-primary focus:border-primary">
            <option>A</option>
          </select>
        </div>
      </div>

      <div className="flex flex-1 gap-gutter min-h-0 overflow-hidden pb-4">
        
        {/* Timetable Grid */}
        <div className="flex-1 bg-surface-container-lowest border border-outline-variant rounded-xl shadow-sm overflow-hidden flex flex-col min-w-[600px]">
          {/* Header Row */}
          <div className="grid grid-cols-6 border-b border-outline-variant bg-surface-container-low text-center font-label-md text-on-surface-variant py-3 shrink-0">
            <div className="border-r border-outline-variant"></div>
            <div className="border-r border-outline-variant">Monday</div>
            <div className="border-r border-outline-variant">Tuesday</div>
            <div className="border-r border-outline-variant">Wednesday</div>
            <div className="border-r border-outline-variant">Thursday</div>
            <div>Friday</div>
          </div>
          
          {/* Time Slots */}
          <div className="flex-1 overflow-y-auto">
            {timeSlots.map((time, rowIdx) => (
              <div key={time} className="grid grid-cols-6 border-b border-outline-variant min-h-[80px]">
                <div className="border-r border-outline-variant flex items-center justify-center font-label-md text-on-surface-variant bg-surface-container-low">
                  {time}
                </div>
                {schedule[rowIdx].map((slot, colIdx) => (
                  <div key={colIdx} className={`border-r border-outline-variant p-2 ${colIdx === 4 ? 'border-r-0' : ''}`}>
                    {slot && (
                      <div className="bg-secondary-container/50 border border-secondary-container w-full h-full rounded-md flex flex-col items-center justify-center text-center p-1 cursor-move hover:bg-secondary-container transition-colors">
                        <span className="font-body-sm font-bold text-on-secondary-container">{slot.subject}</span>
                        <span className="text-[10px] text-on-surface-variant">(Room {slot.room})</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>

        {/* Right Sidebar: Subjects & Classrooms */}
        <div className="w-80 bg-surface-container-lowest border border-outline-variant rounded-xl shadow-sm flex flex-col shrink-0">
          <div className="p-4 border-b border-outline-variant bg-surface-container-low">
            <h3 className="font-headline-md text-on-surface mb-1">Subjects & Classrooms</h3>
            <p className="font-body-sm text-on-surface-variant leading-tight">Drag items onto the timetable grid.</p>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-6">
            <div>
              <h4 className="font-label-md text-on-surface-variant mb-3 uppercase tracking-wider">Subjects</h4>
              <div className="grid grid-cols-2 gap-2">
                {subjects.map(sub => (
                  <div key={sub} className="bg-surface-variant/50 border border-outline-variant py-2 px-3 rounded-md text-center font-body-sm font-medium cursor-grab hover:bg-surface-variant transition-colors">
                    {sub}
                  </div>
                ))}
              </div>
            </div>

            <div className="h-px bg-outline-variant w-full"></div>

            <div>
              <h4 className="font-label-md text-on-surface-variant mb-3 uppercase tracking-wider">Classrooms</h4>
              <div className="grid grid-cols-2 gap-2">
                {rooms.map(room => (
                  <div key={room} className="bg-surface-container border border-outline-variant border-dashed py-2 px-3 rounded-md text-center font-body-sm cursor-grab hover:bg-surface-variant transition-colors">
                    {room}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
