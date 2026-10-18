import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { ChoiceCard } from './ChoiceCard.jsx';

export function QuestionPanel({
  interaction,
  onSubmitResponse,
  onClose,
  isSubmitting,
  displayedAt,
  destinationLabel,
}) {
  const [selectedOptionId, setSelectedOptionId] = useState(null);

  // Reset selection when interaction changes
  useEffect(() => {
    setSelectedOptionId(null);
  }, [interaction?.id]);

  const handleSubmit = () => {
    if (!selectedOptionId) return;

    const submittedAt = performance.now();
    onSubmitResponse({
      optionId: selectedOptionId,
      displayedAt,
      submittedAt,
    });
  };

  if (!interaction) return null;

  const isChoice = interaction.type === 'choice';
  const canSubmit = selectedOptionId !== null && !isSubmitting;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      {/* Game-styled question panel */}
      <div
        className="max-w-2xl w-full p-8 space-y-6 rounded-xl shadow-2xl border-4"
        style={{
          background: 'linear-gradient(135deg, #FFF8E7 0%, #F5DEB3 100%)',
          borderColor: '#8B5A00',
        }}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 hover:bg-amber-200 rounded-lg transition-all"
          aria-label="Close"
        >
          <X size={24} className="text-amber-900" />
        </button>

        {/* Header */}
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-amber-700">
            <span className="text-2xl">{interaction.title || '🎯'}</span>
            <span className="text-sm font-semibold uppercase tracking-wide">Exploring: {destinationLabel}</span>
          </div>

          <h2 className="text-3xl font-bold text-amber-950 leading-tight">
            {interaction.question}
          </h2>

          {interaction.helperText && (
            <p className="text-amber-800 text-lg mt-3">{interaction.helperText}</p>
          )}
        </div>

        {/* Divider */}
        <div className="border-t-2 border-amber-300 my-4" />

        {/* Answer Options */}
        {isChoice && interaction.options && (
          <div className="space-y-3">
            {interaction.options.map((option, idx) => (
              <ChoiceCard
                key={option.id}
                option={option}
                index={idx}
                isSelected={selectedOptionId === option.id}
                isSubmitting={isSubmitting}
                onSelect={setSelectedOptionId}
              />
            ))}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3 pt-4 mt-6 border-t-2 border-amber-300">
          <button
            onClick={onClose}
            className="flex-1 px-6 py-3 font-bold text-lg rounded-lg transition-all
              bg-white text-amber-900 border-2 border-amber-300
              hover:bg-amber-50 hover:border-amber-500
              focus:outline-none focus:ring-2 focus:ring-amber-500 focus:ring-offset-2"
          >
            Back
          </button>
          <button
            onClick={handleSubmit}
            disabled={!canSubmit}
            className="flex-1 px-6 py-3 font-bold text-lg rounded-lg transition-all
              bg-gradient-to-r from-amber-500 to-orange-500 text-white
              hover:from-amber-600 hover:to-orange-600
              disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed
              focus:outline-none focus:ring-2 focus:ring-amber-600 focus:ring-offset-2
              uppercase tracking-wide shadow-lg"
          >
            {isSubmitting ? '⏳ Submitting...' : '✓ Continue'}
          </button>
        </div>
      </div>
    </div>
  );
}
