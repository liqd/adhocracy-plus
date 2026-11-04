import { hasValidAnswer, getUnansweredMandatoryQuestions } from '../utils/pollHelpers'
import type { PollQuestion, UserAnswers } from '../types'

const singleQuestion: PollQuestion = {
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

const multipleQuestion: PollQuestion = {
  ...singleQuestion,
  id: 2,
  label: 'Pick many',
  multiple_choice: true
}

const openQuestion: PollQuestion = {
  id: 3,
  label: 'Your thoughts',
  is_open: true,
  multiple_choice: false,
  is_mandatory: true,
  choices: []
}

const optionalQuestion: PollQuestion = {
  ...singleQuestion,
  id: 4,
  label: 'Optional',
  is_mandatory: false
}

describe('hasValidAnswer', () => {
  it('accepts a single choice question with a selected option', () => {
    expect(hasValidAnswer(singleQuestion, { choices: [10] })).toBe(true)
  })

  it('rejects a single choice question without a selected option', () => {
    expect(hasValidAnswer(singleQuestion, { choices: [] })).toBe(false)
    expect(hasValidAnswer(singleQuestion, undefined)).toBe(false)
  })

  it('accepts a multiple choice question with at least one selected option', () => {
    expect(hasValidAnswer(multipleQuestion, { choices: [10, 11], other_choice_answer: 'text' })).toBe(true)
  })

  it('rejects a multiple choice question without a selected option', () => {
    expect(hasValidAnswer(multipleQuestion, { choices: [] })).toBe(false)
  })

  it('accepts an open question with text', () => {
    expect(hasValidAnswer(openQuestion, { open_answer: 'an answer' })).toBe(true)
  })

  it('rejects an open question with whitespace only', () => {
    expect(hasValidAnswer(openQuestion, { open_answer: '   ' })).toBe(false)
    expect(hasValidAnswer(openQuestion, { open_answer: '' })).toBe(false)
  })

  it('rejects the "other" option without text', () => {
    expect(hasValidAnswer(singleQuestion, { choices: [11], other_choice_answer: '' })).toBe(false)
    expect(hasValidAnswer(multipleQuestion, { choices: [10, 11], other_choice_answer: ' ' })).toBe(false)
  })

  it('accepts the "other" option with text', () => {
    expect(hasValidAnswer(singleQuestion, { choices: [11], other_choice_answer: 'my answer' })).toBe(true)
  })

  it('rejects an "other" answer that was entered without selecting the option', () => {
    expect(hasValidAnswer(singleQuestion, { choices: [], other_choice_answer: 'my answer' })).toBe(false)
  })
})

describe('getUnansweredMandatoryQuestions', () => {
  const questions = [singleQuestion, openQuestion, optionalQuestion]

  it('returns all unanswered mandatory questions', () => {
    const userAnswers: UserAnswers = {}
    expect(getUnansweredMandatoryQuestions(questions, userAnswers)).toEqual([singleQuestion, openQuestion])
  })

  it('ignores optional questions', () => {
    const userAnswers: UserAnswers = {
      1: { choices: [10] },
      3: { open_answer: 'an answer' }
    }
    expect(getUnansweredMandatoryQuestions(questions, userAnswers)).toEqual([])
  })

  it('keeps a mandatory question whose answer is invalid', () => {
    const userAnswers: UserAnswers = {
      1: { choices: [11], other_choice_answer: '' },
      3: { open_answer: 'an answer' }
    }
    expect(getUnansweredMandatoryQuestions(questions, userAnswers)).toEqual([singleQuestion])
  })

  it('returns nothing when the poll has no mandatory questions', () => {
    expect(getUnansweredMandatoryQuestions([optionalQuestion], {})).toEqual([])
  })
})
