import { ProgressBar } from './ProgressBar.jsx';

export function GameHUD({ progress, destinationLabel }) {
  return (
    <div
      className="absolute top-6 left-6 right-6 rounded-xl p-6 shadow-xl z-10 max-w-md"
      style={{
        background: 'linear-gradient(135deg, #FFF8E7 0%, #F5DEB3 100%)',
        borderLeft: '6px solid #8B5A00',
        borderBottom: '3px solid #6B4423',
      }}
    >
      <div className="space-y-4">
        {/* Title */}
        <div className="text-center">
          <h3 className="text-2xl font-black text-amber-950 uppercase tracking-wide">
            ChocoWarm Journey ☕
          </h3>
        </div>

        {/* Progress Bar */}
        <ProgressBar completed={progress.completed} total={progress.total} />

        {/* Current Location */}
        {destinationLabel && (
          <div
            className="text-center rounded-lg p-3"
            style={{
              background: 'rgba(139, 90, 0, 0.1)',
              borderLeft: '4px solid #D4A574',
            }}
          >
            <p className="text-xs font-bold text-amber-700 uppercase tracking-wider">Exploring</p>
            <p className="text-lg font-bold text-amber-950">{destinationLabel}</p>
          </div>
        )}

        {/* Tips */}
        <div className="text-center text-xs text-amber-700 font-bold pt-2">
          💡 Use arrow keys or click doors to explore
        </div>
      </div>
    </div>
  );
}
