import { useCallback, useEffect, useMemo, useState } from 'react';
import RunnerWorld from './components/RunnerWorld.jsx';
import { ArrowLeft, ArrowRight, Volume2, VolumeX, Sparkles, Coffee, Compass, RotateCcw, Timer, Pause, Play } from 'lucide-react';
import { researchService } from './services/index.js';
import './App.css';

const optionColors = ['amber', 'blue', 'violet', 'green'];
const optionSymbols = ['heart', 'energy', 'relax', 'taste'];

function toGameQuestion(question, index) {
  if (!question) return null;

  return {
    id: question.question_id,
    place: `Question ${index + 1}`,
    question: question.text,
    questionType: question.question_type,
    helper: question.question_type === 'price_input'
      ? 'Enter the maximum price you would pay.'
      : question.question_type === 'multiple_choice'
        ? 'Choose one or more answers, then submit.'
        : 'Choose the answer that best fits you.',
    options: (question.options || []).map((option, optionIndex) => ({
      id: option.option_id,
      label: option.label,
      color: optionColors[optionIndex % optionColors.length],
      symbol: optionSymbols[optionIndex % optionSymbols.length],
    })),
  };
}

function App() {
  const [screen, setScreen] = useState('welcome');
  const [question, setQuestion] = useState(null);
  const [selected, setSelected] = useState(null);
  const [transitioning, setTransitioning] = useState(false);
  const [answers, setAnswers] = useState([]);
  const [soundOn, setSoundOn] = useState(false);
  const [characterId, setCharacterId] = useState('boy');
  const [sessionId, setSessionId] = useState(null);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isStarting, setIsStarting] = useState(false);
  const [responseSaved, setResponseSaved] = useState(false);
  const [gameRunId, setGameRunId] = useState(0);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [timerPaused, setTimerPaused] = useState(false);
  const [priceAnswer, setPriceAnswer] = useState('');
  const [completionStatus, setCompletionStatus] = useState('completed');
  const [error, setError] = useState('');
  const current = useMemo(
    () => toGameQuestion(question, Math.max(answers.length - Number(responseSaved), 0)),
    [question, answers.length, responseSaved],
  );
  const progress = useMemo(
    () => ({ completed: answers.length, total: totalQuestions }),
    [answers.length, totalQuestions],
  );
  const formattedTime = `${String(Math.floor(elapsedSeconds / 60)).padStart(2, '0')}:${String(elapsedSeconds % 60).padStart(2, '0')}`;

  const startJourney = async () => {
    setScreen('character');
    setError('');
  };

  const chooseDoor = useCallback((option) => {
    if (transitioning || isSubmitting || responseSaved) return;
    if (current?.questionType === 'multiple_choice') {
      setSelected((previous) => {
        const selections = Array.isArray(previous) ? previous : [];
        return selections.some((item) => item.id === option.id)
          ? selections.filter((item) => item.id !== option.id)
          : [...selections, option];
      });
      return;
    }
    if (selected) return;
    setSelected(option);
  }, [current?.questionType, isSubmitting, responseSaved, selected, transitioning]);

  const beginAdventure = async () => {
    setIsStarting(true);
    setError('');
    setAnswers([]);
    setSelected(null);
    setQuestion(null);
    setSessionId(null);
    setTotalQuestions(0);
    setPriceAnswer('');
    setResponseSaved(false);
    setElapsedSeconds(0);
    setTimerPaused(false);
    try {
      const session = await researchService.startSession();
      const firstQuestion = await researchService.getNextQuestion({
        sessionId: session.sessionId,
      });
      setSessionId(session.sessionId);
      setTotalQuestions(session.totalQuestions);
      setQuestion(firstQuestion.next_question);
      setCompletionStatus(firstQuestion.status);
      setScreen(firstQuestion.next_question ? 'game' : 'complete');
    } catch (startError) {
      setError(startError.message);
    } finally {
      setIsStarting(false);
    }
  };

  useEffect(() => {
    if (screen !== 'game' || timerPaused) return undefined;
    const timerId = window.setInterval(() => {
      setElapsedSeconds((seconds) => seconds + 1);
    }, 1000);
    return () => window.clearInterval(timerId);
  }, [screen, timerPaused]);

  const enterDoor = async () => {
    if (!current || !sessionId || isSubmitting || timerPaused) return;
    const selections = Array.isArray(selected) ? selected : selected ? [selected] : [];
    const numericPrice = Number(priceAnswer);
    let answerSaved = responseSaved;
    if (!answerSaved && current.questionType === 'price_input') {
      if (!priceAnswer || !Number.isFinite(numericPrice) || numericPrice < 0) return;
    } else if (!answerSaved && selections.length === 0) {
      return;
    }

    setTransitioning(!answerSaved && !isManualQuestion);
    setIsSubmitting(true);
    setError('');
    try {
      if (!answerSaved && !isManualQuestion) {
        await new Promise((resolve) => window.setTimeout(resolve, 700));
      }
      if (!answerSaved) {
        const payload = {
          sessionId,
          questionId: current.id,
          ...(current.questionType === 'price_input'
            ? { answerValue: numericPrice }
            : current.questionType === 'multiple_choice'
              ? { answerValue: selections.map((option) => option.id) }
              : { optionId: selections[0].id }),
        };
        await researchService.submitResponse(payload);
        answerSaved = true;
        setResponseSaved(true);
        setAnswers((previous) => [
          ...previous,
          {
            questionId: current.id,
            question: current.question,
            answer: current.questionType === 'price_input'
              ? `₹${numericPrice}`
              : selections.map((option) => option.label).join(', '),
          },
        ]);
      }
      const next = await researchService.getNextQuestion({ sessionId });
      setResponseSaved(false);
      setSelected(null);
      setPriceAnswer('');
      setQuestion(next.next_question);
      setCompletionStatus(next.status);
      setGameRunId((previous) => previous + 1);
      setScreen(next.next_question ? 'game' : 'complete');
    } catch (submitError) {
      setError(submitError.message);
      if (!answerSaved) {
        setSelected(null);
        setGameRunId((previous) => previous + 1);
      }
    } finally {
      setTransitioning(false);
      setIsSubmitting(false);
    }
  };

  const goBack = useCallback(() => {
    if (!transitioning && !isSubmitting && answers.length === 0) {
      setScreen('character');
    }
  }, [answers.length, isSubmitting, transitioning]);

  useEffect(() => {
    const handleKey = (event) => {
      if (screen !== 'game' || transitioning || timerPaused || !current) return;
      if (/^[1-9]$/.test(event.key)) {
        const option = current.options[Number(event.key) - 1];
        if (option) chooseDoor(option);
      }
      if (event.key === 'Escape') goBack();
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [chooseDoor, current, goBack, screen, timerPaused, transitioning]);

  const selectedOptions = Array.isArray(selected) ? selected : selected ? [selected] : [];
  const isMultipleChoice = current?.questionType === 'multiple_choice';
  const isManualQuestion = isMultipleChoice || current?.questionType === 'price_input';
  const canSubmitManual = isMultipleChoice
    ? selectedOptions.length > 0
    : Boolean(priceAnswer) && Number.isFinite(Number(priceAnswer)) && Number(priceAnswer) >= 0;
  const selectionLabel = current?.questionType === 'price_input'
    ? (priceAnswer ? `₹${priceAnswer}` : 'Enter a price')
    : selectedOptions.length
      ? selectedOptions.map((option) => option.label).join(', ')
      : 'Choose an answer';

  return <main className={`game-shell ${transitioning ? 'scene-transitioning' : ''}`}>
    <div className="world-backdrop" />
    <div className="world-vignette" />
    <header className="top-hud">
      <button className="brand-mark" onClick={() => setScreen('welcome')} aria-label="ChocoWarm home"><span className="brand-heart">H</span><span><strong>ChocoWarm</strong><small>Your Hot Chocolate</small></span></button>
      {screen === 'game' && <div className="journey-meter"><div className="meter-title"><Sparkles size={17}/><span>Survey progress</span><b>{progress.completed}/{progress.total}</b></div><div className="meter-track"><span style={{ width: `${progress.total ? (progress.completed / progress.total) * 100 : 0}%` }}/></div></div>}
      <div className="top-actions">{screen === 'game' && <><div className="game-clock"><Timer size={16}/><span>{formattedTime}</span></div><button className="timer-toggle" onClick={() => setTimerPaused((paused) => !paused)} aria-label={timerPaused ? 'Resume game timer' : 'Pause game timer'}>{timerPaused ? <Play size={17}/> : <Pause size={17}/>}<span>{timerPaused ? 'Resume' : 'Pause'}</span></button><div className="spark-counter"><Sparkles size={16}/><span>{answers.length} stars</span></div></>}<button className="round-control" onClick={() => setSoundOn(v => !v)} aria-label={soundOn ? 'Turn sound off' : 'Turn sound on'}>{soundOn ? <Volume2/> : <VolumeX/>}</button></div>
    </header>

    {screen === 'welcome' && <section className="welcome-scene"><div className="welcome-copy"><h1>Choose your<br/><em>hot chocolate moment</em></h1><p>Answer a few quick questions and discover your perfect cup.</p><button className="gold-cta" onClick={startJourney}>Lets go <ArrowRight size={18}/></button><div className="welcome-meta"><span>About 5 minutes</span><span>25 questions</span></div></div><div className="welcome-character welcome-emoji"></div><div className="welcome-hint"><Compass size={17}/> Your answer matters</div></section>}

    {screen === 'character' && <section className="character-select-scene"><div className="character-select-copy"><h1>Choose your<br/><em>runner</em></h1><p>Pick a character for your hot chocolate adventure.</p></div><div className="character-options">{[{id:'boy',name:'The Explorer',desc:'Brave, curious, ready to discover',avatar:'🧑‍🦰',tone:'blue'},{id:'girl',name:'The Adventurer',desc:'Energetic, daring, full of spirit',avatar:'👩‍🦱',tone:'pink'}].map(c=><button key={c.id} className={`character-choice ${characterId===c.id?'character-choice-active':''} character-${c.tone}`} onClick={()=>setCharacterId(c.id)}><span className="character-art character-emoji" aria-hidden="true">{c.avatar}</span><strong>{c.name}</strong><small>{c.desc}</small><span className="character-select-status">{characterId===c.id?'Selected':'Choose'}</span></button>)}</div>{error && <div className="inline-error character-error">{error}</div>}<div className="character-select-bottom"><button className="gold-cta" onClick={beginAdventure} disabled={isStarting}>{isStarting ? 'Connecting...' : 'Start journey'} <ArrowRight size={18}/></button></div></section>}

    {screen === 'game' && current && <section className="game-scene">
      <div className="question-banner"><div className="question-cup"><Coffee size={27}/></div><div className="question-content"><span className="eyebrow">{current.place}</span><h2>{current.question}</h2><p>{current.helper}</p></div><span className="question-glint glint-left">*</span><span className="question-glint glint-right">*</span></div>
      {current.questionType === 'price_input' ? <div className="price-answer-panel"><label htmlFor="price-answer">Your price in rupees</label><input id="price-answer" type="number" min="0" step="0.01" value={priceAnswer} onChange={(event) => setPriceAnswer(event.target.value)} disabled={isSubmitting || responseSaved || timerPaused} /></div> : <>
        <RunnerWorld characterId={characterId} options={current.options} selected={selected} multiSelect={isMultipleChoice} isPaused={timerPaused} onChoose={chooseDoor} sceneKey={`${current.id}-${gameRunId}`} />
        <div className="game-options" aria-label="Answer options">{current.options.map((option, index) => {
          const isSelected = selectedOptions.some((item) => item.id === option.id);
          return <button key={option.id} type="button" className={`game-option option-${option.color} ${isSelected ? 'game-option-selected' : ''}`} onClick={() => chooseDoor(option)} disabled={isSubmitting || transitioning || timerPaused || responseSaved} aria-pressed={isSelected}><span className="option-number">{index + 1}</span><span className="option-label">{option.label}</span>{isSelected && <span className="option-check">✓</span>}</button>;
        })}</div>
      </>}
      <div className="scene-footer"><button className="round-back" onClick={goBack} aria-label="Go back" disabled={answers.length > 0 || isSubmitting}><ArrowLeft size={21}/></button><div className="place-chip"><span className="place-icon"><Compass size={25}/></span><span><strong>{current.place}</strong><small>{selectionLabel}</small></span></div><div className="move-hint">{current.options.slice(0, 5).map((option, index) => <span className="keycap" key={option.id}>{index + 1}</span>)}<small>{isMultipleChoice ? 'Select answers' : 'Choose'}</small></div><button className="enter-cta" onClick={enterDoor} disabled={isSubmitting || transitioning || (!responseSaved && (isManualQuestion ? !canSubmitManual : selectedOptions.length === 0))}>{isSubmitting ? 'Saving...' : responseSaved ? 'Retry' : isManualQuestion ? 'Submit answer' : transitioning ? 'Running...' : selected ? 'Enter selected gate' : 'Choose gate'} <ArrowRight size={17}/></button></div>
      {transitioning && <div className="runner-status"><span className="runner-status-dot"/> Running to: {selectionLabel}</div>}
      {error && <div className="inline-error">{error}</div>}
      {timerPaused && <div className="pause-shade"><section className="pause-card"><span className="eyebrow">TAKE A BREATHER</span><h2>Adventure paused</h2><p>Your timer and the world are paused. Pick up where you left off whenever you’re ready.</p><button className="gold-cta" onClick={() => setTimerPaused(false)}><Play size={17}/> Resume adventure</button></section></div>}
    </section>}

    {screen === 'complete' && <section className="complete-scene"><div className="reward-orbit"><Sparkles size={68}/></div><span className="eyebrow">{completionStatus === 'ineligible' ? 'THANK YOU' : 'JOURNEY COMPLETE'}</span><h1>{completionStatus === 'ineligible' ? <>Thanks for<br/><em>your interest</em></> : <>You helped shape<br/><em>something warmer</em></>}</h1><p>{completionStatus === 'ineligible' ? 'This survey is intended for respondents aged 18 and above.' : 'Thank you for sharing your hot chocolate preferences.'}</p><div className="completion-stats"><span><strong>{answers.length}</strong><small>answers</small></span><span><strong>{totalQuestions}</strong><small>questions</small></span><span><strong>H</strong><small>impact</small></span></div><button className="gold-cta" onClick={() => { setScreen('welcome'); setQuestion(null); setSessionId(null); setTotalQuestions(0); setAnswers([]); setSelected(null); setError(''); }}>Play again <RotateCcw size={17}/></button></section>}
    <div className="bottom-slogan"><span>*</span> SMALL CHOICES BIG DIFFERENCE <span>*</span></div>
  </main>;
}
export default App;
