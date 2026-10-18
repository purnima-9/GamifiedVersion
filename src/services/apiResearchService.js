const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
).replace(/\/$/, '');

const researchDimensions = [
  { name: 'Overall appeal', importance: 8, target_coverage: 0.8 },
  { name: 'Consumption occasions', importance: 7, target_coverage: 0.75 },
  { name: 'Flavor preferences', importance: 8, target_coverage: 0.8 },
  { name: 'Sweetness preference', importance: 6, target_coverage: 0.7 },
  { name: 'Cocoa intensity preference', importance: 7, target_coverage: 0.75 },
  { name: 'Milk and base preference', importance: 6, target_coverage: 0.7 },
  { name: 'Topping preferences', importance: 5, target_coverage: 0.65 },
  { name: 'Serving temperature', importance: 5, target_coverage: 0.65 },
  { name: 'Serving size preference', importance: 5, target_coverage: 0.65 },
  { name: 'Purchase frequency', importance: 7, target_coverage: 0.75 },
  { name: 'Purchase intent', importance: 9, target_coverage: 0.85 },
  { name: 'Price willingness', importance: 9, target_coverage: 0.85 },
  { name: 'Value for money', importance: 8, target_coverage: 0.8 },
  { name: 'Preferred purchase location', importance: 6, target_coverage: 0.7 },
  { name: 'Product convenience', importance: 6, target_coverage: 0.7 },
  { name: 'Ingredient expectations', importance: 7, target_coverage: 0.75 },
  { name: 'Sugar and health perception', importance: 7, target_coverage: 0.75 },
  { name: 'Brand trust', importance: 6, target_coverage: 0.7 },
  { name: 'Packaging preference', importance: 5, target_coverage: 0.65 },
  { name: 'Sustainability importance', importance: 5, target_coverage: 0.65 },
  { name: 'Sharing and social occasions', importance: 5, target_coverage: 0.65 },
  { name: 'Product discovery channel', importance: 6, target_coverage: 0.7 },
  { name: 'Likelihood to recommend', importance: 7, target_coverage: 0.75 },
  { name: 'Product improvements', importance: 6, target_coverage: 0.7 },
];

async function request(path, options = {}) {
  let response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        ...(options.body ? { 'Content-Type': 'application/json' } : {}),
        ...options.headers,
      },
    });
  } catch (error) {
    throw new Error(
      `Cannot connect to the survey API at ${API_BASE_URL}. Start the adaptive survey backend and check VITE_API_BASE_URL.`,
      { cause: error },
    );
  }

  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = payload?.detail;
    const message = Array.isArray(detail)
      ? detail.map((item) => item.msg).join(', ')
      : detail || `Survey API request failed (${response.status}).`;
    throw new Error(message);
  }

  return payload;
}

export const apiResearchService = {
  async startSession() {
    const research = await request('/api/v1/research', {
      method: 'POST',
      body: JSON.stringify({
        topic: 'Premium hot chocolate',
        target_audience: 'Hot chocolate consumers aged 18 and above',
        geography: 'India',
        dimensions: researchDimensions,
      }),
    });

    const session = await request(
      `/api/v1/research/${research.id}/sessions?max_questions=25`,
      { method: 'POST' },
    );

    return {
      sessionId: session.session_id,
      researchId: session.research_id,
      totalQuestions: session.total_questions,
      surveyTitle: research.topic,
    };
  },

  getNextQuestion({ sessionId }) {
    return request(`/api/v1/sessions/${sessionId}/next`);
  },

  submitResponse({ sessionId, questionId, optionId, answerValue }) {
    return request(`/api/v1/sessions/${sessionId}/responses`, {
      method: 'POST',
      body: JSON.stringify({
        question_id: questionId,
        ...(optionId ? { option_id: optionId } : {}),
        ...(answerValue !== undefined ? { answer_value: answerValue } : {}),
      }),
    });
  },
};
