// apps/polls/assets/react_poll_management/utils.ts
import type { ManagementChoice, ManagementQuestion } from './types'

let maxLocalKey = 0

export const getNextLocalKey = (): string => `local_${maxLocalKey++}`

/** Only used in tests to make generated keys deterministic. */
export const resetLocalKeys = (): void => {
  maxLocalKey = 0
}

export const createEmptyChoice = (isOther = false): ManagementChoice => ({
  key: getNextLocalKey(),
  label: isOther ? 'other' : '',
  is_other_choice: isOther
})

export const createEmptyQuestion = (isOpen: boolean): ManagementQuestion => ({
  key: getNextLocalKey(),
  label: '',
  help_text: '',
  multiple_choice: false,
  is_open: isOpen,
  is_confidential: false,
  choices: isOpen ? [] : [createEmptyChoice(), createEmptyChoice()],
  image_base64: null,
  image_url: null,
  image_alt_text: ''
})

/**
 * Questions returned by the poll API are enriched with read-only fields
 * (userChoices, vote counts, ...). Attach stable local keys so the
 * management UI can track items (also unsaved ones) without ids.
 */
export const normalizeQuestion = (question: any): ManagementQuestion => ({
  ...question,
  key: question.id != null ? `q_${question.id}` : getNextLocalKey(),
  choices: (question.choices || []).map((choice: any) => ({
    ...choice,
    key: choice.id != null ? `c_${choice.id}` : getNextLocalKey()
  }))
})

export const cloneQuestion = (question: ManagementQuestion): ManagementQuestion =>
  JSON.parse(JSON.stringify(question)) as ManagementQuestion

const READ_ONLY_QUESTION_FIELDS = [
  'key',
  'answers',
  'image_url',
  'image_help_text',
  'userChoices',
  'userAnswer',
  'other_choice_answers',
  'other_choice_user_answer',
  'totalVoteCount',
  'totalVoteCountMulti',
  'totalAnswerCount',
  'isReadOnly',
  'authenticated',
  'count'
]

const READ_ONLY_CHOICE_FIELDS = ['key', 'count']

/**
 * Build the questions payload for the poll update API.
 * Read-only fields coming from the API are stripped so the request body
 * only contains what the backend serializer/service understands.
 */
export const buildQuestionsPayload = (questions: ManagementQuestion[]) =>
  questions.map((question) => {
    const source = question as unknown as Record<string, unknown>
    const payload: Record<string, unknown> = {}

    Object.keys(source).forEach((field) => {
      if (!READ_ONLY_QUESTION_FIELDS.includes(field)) {
        payload[field] = source[field]
      }
    })

    payload.choices = ((source.choices || []) as Array<Record<string, unknown>>)
      .map((choice) => {
        const cleanChoice: Record<string, unknown> = {}
        Object.keys(choice).forEach((field) => {
          if (!READ_ONLY_CHOICE_FIELDS.includes(field)) {
            cleanChoice[field] = choice[field]
          }
        })
        return cleanChoice
      })

    if (source.image_base64 !== undefined) {
      payload.image_base64 = source.image_base64
    }
    payload.image_alt_text = source.image_alt_text || ''
    return payload
  })

export const moveItem = <T>(items: T[], from: number, to: number): T[] => {
  if (from === to || from < 0 || to < 0 || from >= items.length || to >= items.length) {
    return items
  }
  const result = [...items]
  const [moved] = result.splice(from, 1)
  result.splice(to, 0, moved)
  return result
}
