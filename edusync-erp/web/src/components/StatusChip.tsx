interface StatusChipProps {
  status: 'pending' | 'submitted' | 'graded' | 'scheduled' | 'completed' | 'processing';
}

export default function StatusChip({ status }: StatusChipProps) {
  const colorMap: Record<string, string> = {
    pending: 'bg-tertiary-container text-on-tertiary-container',
    submitted: 'bg-secondary-container text-on-secondary-container',
    graded: 'bg-primary-container text-on-primary-container',
    scheduled: 'bg-surface-variant text-on-surface-variant',
    completed: 'bg-primary-container text-on-primary-container',
    processing: 'bg-secondary-container text-on-secondary-container'
  };

  return (
    <span className={`px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider ${colorMap[status]}`}>
      {status}
    </span>
  );
}
