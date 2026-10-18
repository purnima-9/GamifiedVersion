export function ProgressBar({ completed, total }) {
  const percentage = total > 0 ? (completed / total) * 100 : 0;

  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center">
        <span className="text-sm font-bold text-amber-900 uppercase">Progress</span>
        <span className="text-sm font-bold text-amber-900">
          {completed} <span className="text-amber-700">/</span> {total}
        </span>
      </div>

      {/* Progress bar with border */}
      <div
        className="w-full h-4 rounded-full overflow-hidden border-2"
        style={{
          background: '#F5DEB3',
          borderColor: '#8B5A00',
          boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.1)',
        }}
      >
        <div
          className="h-full rounded-full transition-all duration-500 ease-out"
          style={{
            width: `${percentage}%`,
            background: 'linear-gradient(90deg, #FFD700 0%, #FFA500 100%)',
            boxShadow: `0 0 8px rgba(255, 165, 0, 0.6)`,
          }}
        />
      </div>

      {/* Stage indicator */}
      <div className="flex gap-2 justify-center pt-1">
        {[...Array(total)].map((_, i) => (
          <div
            key={i}
            className="w-2 h-2 rounded-full transition-all"
            style={{
              background: i < completed ? '#FFD700' : '#D4A574',
              opacity: i < completed ? 1 : 0.5,
            }}
          />
        ))}
      </div>
    </div>
  );
}
