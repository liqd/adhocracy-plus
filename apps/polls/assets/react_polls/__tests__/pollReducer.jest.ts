import { pollReducer, initialState } from '../reducers/pollReducer'
import { ACTIONS, STATES } from '../utils/stateMachine'
import type { PollQuestion, PollState } from '../types'

const MESSAGE = 'Please answer this question to continue.'

const mandatoryQuestion: PollQuestion = {
  id: 1,
  label: 'Pick one',
  is_open: false,
  multiple_choice: false,
  is_mandatory: true,
  choices: [
    { id: 10, label: 'Red', is_other_choice: false },
    { id: 11, label: 'Other', is_other_choice: true }
  ]
}

const secondMandatoryQuestion: PollQuestion = {
  ...mandatoryQuestion,
  id: 2,
  label: 'Your thoughts',
  is_open: true,
  choices: []
}

const answeringState: PollState = {
  ...initialState,
  state: STATES.ANSWERING,
  isLoading: false,
  questions: [mandatoryQuestion, secondMandatoryQuestion]
}

describe('pollReducer mandatory question errors', () => {
  it('adds an error for every unanswered mandatory question', () => {
    const state = pollReducer(answeringState, {
      type: ACTIONS.SET_QUESTION_ERRORS,
      payload: { questionIds: [1, 2], message: MESSAGE }
    })

    expect(state.errors).toEqual({ 1: [MESSAGE], 2: [MESSAGE] })
  })

  it('keeps the errors of the other questions when one is answered', () => {
    const withErrors = pollReducer(answeringState, {
      type: ACTIONS.SET_QUESTION_ERRORS,
      payload: { questionIds: [1, 2], message: MESSAGE }
    })

    const state = pollReducer(withErrors, {
      type: ACTIONS.UPDATE_ANSWER,
      payload: { questionId: 1, answerData: { choices: [10] } }
    })

    expect(state.errors).toEqual({ 2: [MESSAGE] })
  })

  it('keeps the error while an answer is still invalid', () => {
    const withErrors = pollReducer(answeringState, {
      type: ACTIONS.SET_QUESTION_ERRORS,
      payload: { questionIds: [1, 2], message: MESSAGE }
    })

    const state = pollReducer(withErrors, {
      type: ACTIONS.UPDATE_ANSWER,
      payload: { questionId: 1, answerData: { choices: [11], other_choice_answer: '' } }
    })

    expect(state.errors).toEqual({ 1: [MESSAGE], 2: [MESSAGE] })
  })

  it('keeps the error for an open question that only contains whitespace', () => {
    const withErrors = pollReducer(answeringState, {
      type: ACTIONS.SET_QUESTION_ERRORS,
      payload: { questionIds: [2], message: MESSAGE }
    })

    const state = pollReducer(withErrors, {
      type: ACTIONS.UPDATE_ANSWER,
      payload: { questionId: 2, answerData: { open_answer: '   ' } }
    })

    expect(state.errors).toEqual({ 2: [MESSAGE] })
  })

  it('jumps to the first unanswered mandatory question', () => {
    const state = pollReducer(answeringState, {
      type: ACTIONS.GO_TO_QUESTION,
      payload: 1
    })

    expect(state.currentQuestionIndex).toBe(1)
  })

  it('clears all errors when the poll is started again', () => {
    const startScreenState: PollState = {
      ...answeringState,
      state: STATES.START_SCREEN,
      errors: { 1: [MESSAGE] }
    }

    const state = pollReducer(startScreenState, { type: ACTIONS.START_POLL })

    expect(state.errors).toEqual({})
  })
})
