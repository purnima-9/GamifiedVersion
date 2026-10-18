export function ChoiceCard({ option, index, isSelected, isSubmitting, onSelect }) {
  const colors = ['#FF6B6B', '#4ECDC4', '#FFE66D'];
  const accentColor = colors[index % colors.length];

  return (
    <button
      onClick={() => onSelect(option.id)}
      disabled={isSubmitting}
      className={`
        w-full px-6 py-4 rounded-lg font-bold text-lg
        transition-all duration-200 ease-out
        border-3 border-amber-300
        focus:outline-none focus:ring-2 focus:ring-amber-600 focus:ring-offset-2
        disabled:opacity-50 disabled:cursor-not-allowed
        transform hover:scale-102
        ${
          isSelected
            ? 'shadow-lg'
            : 'hover:shadow-md'
        }
      `}
      style={{
        background: isSelected
          ? `linear-gradient(135deg, ${accentColor} 0%, ${accentColor}DD 100%)`
          : 'linear-gradient(135deg, #FFFACD 0%, #FFE4B5 100%)',
        color: isSelected ? '#fff' : '#3D2817',
        borderColor: accentColor,
        boxShadow: isSelected ? `0 8px 16px ${accentColor}44` : '0 2px 4px rgba(0,0,0,0.1)',
      }}
      aria-pressed={isSelected}
    >
      <span className="text-3xl mr-3">{index + 1}.</span>
      {option.label}
    </button>
  );
}
