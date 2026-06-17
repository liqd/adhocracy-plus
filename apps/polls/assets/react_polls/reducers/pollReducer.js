// apps/polls/assets/react_polls/reducers/pollReducer.js
import { STATES, ACTIONS, isValidTransition } from '../utils/stateMachine'

export const initialState = {
  // Machine state
  state: STATES.LOADING,

  // Navigation
  currentQuestionIndex: 0,

  // Data
  questions: [],
  userAnswers: {},
  results: [],

  // Permissions & Settings
  allowUnregisteredUsers: false,
  isAuthenticated: false,
  hasUserVote: false,
  useTermsOfUse: false,
  agreedTermsOfUse: false,
  orgTermsUrl: '',

  // UI State
  alert: null,
  checkedTermsOfUse: false,
  errors: {},
  isLoading: true,
  isSubmitting: false,

  // Captcha
  captcha: '',
  refreshCaptcha: 0,
  captchaEnabled: false,
  prosopoSiteKey: ''
}

const reducers = {
  [ACTIONS.DATA_LOADED]: (state, payload) => ({
    ...state,
    questions: payload.questions,
    userAnswers: payload.userAnswers,
    results: payload.results,
    allowUnregisteredUsers: payload.allowUnregisteredUsers,
    isAuthenticated: payload.isAuthenticated,
    hasUserVote: payload.hasUserVote,
    useTermsOfUse: payload.useTermsOfUse,
    agreedTermsOfUse: payload.agreedTermsOfUse,
    orgTermsUrl: payload.orgTermsUrl,
    state: payload.hasUserVote ? STATES.RESULTS : STATES.START_SCREEN,
    isLoading: false
  }),

  [ACTIONS.DATA_ERROR]: (state, payload) => ({
    ...state,
    state: STATES.ERROR,
    alert: payload,
    isLoading: false
  }),

  [ACTIONS.START_POLL]: (state) => ({
    ...state,
    state: STATES.ANSWERING,
    currentQuestionIndex: 0,
    alert: null
  }),

  [ACTIONS.NEXT_QUESTION]: (state) => {
    if (state.currentQuestionIndex >= state.questions.length - 1) return state
    return {
      ...state,
      currentQuestionIndex: state.currentQuestionIndex + 1,
      alert: null
    }
  },

  [ACTIONS.PREV_QUESTION]: (state) => {
    if (state.currentQuestionIndex <= 0) return state
    return {
      ...state,
      currentQuestionIndex: state.currentQuestionIndex - 1,
      alert: null
    }
  },

  [ACTIONS.SKIP_QUESTION]: (state) => {
    if (state.currentQuestionIndex >= state.questions.length - 1) return state
    return {
      ...state,
      currentQuestionIndex: state.currentQuestionIndex + 1,
      alert: null
    }
  },

  [ACTIONS.UPDATE_ANSWER]: (state, { questionId, answerData }) => ({
    ...state,
    userAnswers: {
      ...state.userAnswers,
      [questionId]: {
        ...state.userAnswers[questionId],
        ...answerData
      }
    }
  }),

  [ACTIONS.SUBMIT_START]: (state) => ({
    ...state,
    state: STATES.SUBMITTING,
    isSubmitting: true,
    checkedTermsOfUse: false
  }),

  [ACTIONS.SUBMIT_SUCCESS]: (state, payload) => ({
    ...state,
    state: STATES.RESULTS,
    results: payload.results,
    questions: payload.questions,
    hasUserVote: true,
    useTermsOfUse: payload.useTermsOfUse,
    agreedTermsOfUse: payload.agreedTermsOfUse,
    orgTermsUrl: payload.orgTermsUrl,
    isSubmitting: false,
    alert: payload.alert
  }),

  [ACTIONS.SUBMIT_ERROR]: (state, payload) => ({
    ...state,
    state: STATES.ANSWERING,
    isSubmitting: false,
    alert: payload,
    refreshCaptcha: state.refreshCaptcha + 1
  }),

  [ACTIONS.SET_ALERT]: (state, payload) => ({
    ...state,
    alert: payload
  }),

  [ACTIONS.CLEAR_ALERT]: (state) => ({
    ...state,
    alert: null
  }),

  [ACTIONS.SET_CHECKED_TERMS]: (state, payload) => ({
    ...state,
    checkedTermsOfUse: payload
  }),

  [ACTIONS.SET_CAPTCHA]: (state, payload) => ({
    ...state,
    captcha: payload
  }),

  [ACTIONS.BACK_TO_POLL]: (state) => ({
    ...state,
    state: STATES.START_SCREEN,
    currentQuestionIndex: 0
  }),

  [ACTIONS.CHANGE_ANSWER]: (state) => ({
    ...state,
    state: STATES.ANSWERING,
    currentQuestionIndex: 0
  })
}

export const pollReducer = (state, action) => {
  if (!isValidTransition(state.state, action.type)) {
    console.warn(`Invalid transition: ${state.state} -> ${action.type}`)
    return state
  }

  const reducer = reducers[action.type]
  if (!reducer) {
    console.warn(`Unknown action type: ${action.type}`)
    return state
  }

  return reducer(state, action.payload ?? action.payload)
}
