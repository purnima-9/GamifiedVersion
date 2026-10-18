export function CompletionScreen({ reward, onRestart }) {
  return (
    <div className="fixed inset-0 bg-gradient-to-b from-purple-900 to-indigo-900 flex items-center justify-center p-4 z-50">
      {/* Celebration particles background */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        {[...Array(8)].map((_, i) => (
          <div
            key={i}
            className="absolute animate-bounce text-4xl"
            style={{
              left: `${20 + i * 12}%`,
              top: `-20px`,
              animation: `bounce 2s ease-in-out ${i * 0.2}s infinite`,
            }}
          >
            ✨
          </div>
        ))}
      </div>

      {/* Reward Card */}
      <div
        className="max-w-2xl w-full p-12 rounded-2xl shadow-2xl border-4 space-y-8 relative z-10 text-center"
        style={{
          background: 'linear-gradient(135deg, #FFD700 0%, #FFA500 50%, #FF8C00 100%)',
          borderColor: '#B8860B',
        }}
      >
        {/* Celebration emoji */}
        <div className="text-7xl animate-bounce">🎉</div>

        {/* Title */}
        <div className="space-y-2">
          <h2 className="text-4xl font-black text-amber-950 uppercase tracking-widest">
            {reward?.label || 'Journey Complete!'}
          </h2>
          {reward?.message && (
            <p className="text-xl text-amber-900 font-bold">{reward.message}</p>
          )}
        </div>

        {/* Non-redeemable notice */}
        {reward?.redeemable === false && (
          <div
            className="border-3 rounded-lg p-6 text-amber-900 font-bold"
            style={{
              background: 'rgba(255, 255, 255, 0.5)',
              borderColor: '#8B5A00',
            }}
          >
            <p className="text-lg">
              🎮 <strong>Demo Reward</strong>
            </p>
            <p className="text-sm mt-2">
              This is a non-redeemable demo reward created for testing purposes.
            </p>
          </div>
        )}

        {/* Progress summary */}
        <div className="text-amber-950 font-bold text-lg">
          <p>✓ You've completed the ChocoWarm research journey</p>
          <p className="text-sm mt-2">Thank you for sharing your hot chocolate preferences!</p>
        </div>

        {/* Restart button */}
        <button
          onClick={onRestart}
          className="w-full px-8 py-4 font-bold text-xl rounded-xl transition-all
            bg-gradient-to-r from-purple-600 to-indigo-600 text-white
            hover:from-purple-700 hover:to-indigo-700
            focus:outline-none focus:ring-4 focus:ring-purple-400 focus:ring-offset-2
            uppercase tracking-wide shadow-lg transform hover:scale-105"
        >
          🔄 Start Another Journey
        </button>
      </div>

      <style>{`
        @keyframes bounce {
          0%, 100% { transform: translateY(0); opacity: 1; }
          50% { transform: translateY(-200px); opacity: 0.8; }
        }
      `}</style>
    </div>
  );
}
