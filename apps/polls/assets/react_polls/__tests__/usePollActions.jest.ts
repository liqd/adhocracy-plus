import { act, renderHook } from '@testing-library/react'

import { usePollActions } from '../hooks/usePollActions'
import { initialState } from '../reducers/pollReducer'
import { ACTIONS, STATES } from '../utils/stateMachine'
import { MANDATORY_QUESTION_ERROR } from '../utils/alerts'
import type { PollQuestion, PollState } from '../types'

const mandatoryQuestion: PollQuestion = {
  id: 1,
  label: 'Pick one',
  is_open: false,
  multiple_choice: false,
  is_mandatory: true,
  choices: [
    { id: 10, label: 'Red', is_other_choice: false },
    { id: 11, label: 'Blue', is_other_choice: false }
  ]
}

const optionalQuestion: PollQuestion = {
  ...mandatoryQuestion,
  id: 2,
  label: 'Optional',
  is_mandatory: false
}

const baseState: PollState = {
  ...initialState,
  state: STATES.ANSWERING,
  isLoading: false,
  questions: [mandatoryQuestion, optionalQuestion],
  userAnswers: {}
}

const mandatoryErrors = (questionIds: number[]) => ({
  type: ACTIONS.SET_QUESTION_ERRORS,
  payload: { questionIds, message: MANDATORY_QUESTION_ERROR }
})

describe('usePollActions', () => {
  it('blocks Next and marks the mandatory question as unanswered', () => {
    const dispatch = jest.fn()
    const { result } = renderHook(() => usePollActions(baseState, dispatch, 1))

    act(() => result.current.handleNext())

    expect(dispatch).toHaveBeenCalledWith(mandatoryErrors([mandatoryQuestion.id]))
    expect(dispatch).not.toHaveBeenCalledWith({ type: ACTIONS.NEXT_QUESTION })
  })

  it('allows Next once the mandatory question is answered', () => {
    const dispatch = jest.fn()
    const state: PollState = {
      ...baseState,
      userAnswers: { [mandatoryQuestion.id]: { choices: [10] } }
    }
    const { result } = renderHook(() => usePollActions(state, dispatch, 1))

    act(() => result.current.handleNext())

    expect(dispatch).toHaveBeenCalledWith({ type: ACTIONS.NEXT_QUESTION })
    expect(dispatch).not.toHaveBeenCalledWith(mandatoryErrors([mandatoryQuestion.id]))
  })

  it('does not skip a mandatory question', () => {
    const dispatch = jest.fn()
    const { result } = renderHook(() => usePollActions(baseState, dispatch, 1))

    act(() => result.current.handleSkip())

    expect(dispatch).toHaveBeenCalledWith(mandatoryErrors([mandatoryQuestion.id]))
    expect(dispatch).not.toHaveBeenCalledWith({ type: ACTIONS.SKIP_QUESTION })
  })

  it('skips an optional question', () => {
    const dispatch = jest.fn()
    const state: PollState = { ...baseState, currentQuestionIndex: 1 }
    const { result } = renderHook(() => usePollActions(state, dispatch, 1))

    act(() => result.current.handleSkip())

    expect(dispatch).toHaveBeenCalledWith({ type: ACTIONS.SKIP_QUESTION })
  })

  it('blocks the submission and jumps to the first unanswered mandatory question', async () => {
    const dispatch = jest.fn()
    const state: PollState = {
      ...baseState,
      currentQuestionIndex: 1,
      userAnswers: { [optionalQuestion.id]: { choices: [10] } }
    }
    const { result } = renderHook(() => usePollActions(state, dispatch, 1))

    await act(async () => {
      await result.current.handleSubmitAll()
    })

    expect(dispatch).toHaveBeenCalledWith(mandatoryErrors([mandatoryQuestion.id]))
    expect(dispatch).toHaveBeenCalledWith({
      type: ACTIONS.GO_TO_QUESTION,
      payload: 0
    })
    expect(dispatch).not.toHaveBeenCalledWith({ type: ACTIONS.SUBMIT_START })
  })
})
