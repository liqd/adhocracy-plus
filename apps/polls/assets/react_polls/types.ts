export interface PollChoiceData {
  id: number
  label: string
  is_other_choice: boolean
  count?: number
}

export interface PollQuestion {
  id: number
  label: string
  help_text?: string
  is_open: boolean
  is_confidential?: boolean
  multiple_choice: boolean
  choices: PollChoiceData[]
  userChoices?: number[]
  other_choice_answer?: string
  open_answer?: string
  image_url?: string
  image_alt_text?: string
  authenticated?: boolean
  isReadOnly?: boolean
  answers?: PollAnswer[]
  userAnswer?: number
  other_choice_answers?: PollOtherAnswer[]
  other_choice_user_answer?: number
  count?: number
  totalAnswerCount?: number
  totalVoteCount?: number
  totalVoteCountMulti?: number
}

export interface PollAnswer {
  id: number
  answer: string
}

export interface PollOtherAnswer {
  vote_id: number
  answer: string
}

export interface UserAnswer {
  choices?: number[]
  other_choice_answer?: string
  open_answer?: string
}

export type UserAnswers = Record<number, UserAnswer>

export interface AlertState {
  type: string
  message: string
}

export interface PollResultsPayload {
  questions: PollQuestion[]
  hasUserVote: boolean
  votingEnded: boolean
  useTermsOfUse: boolean
  agreedTermsOfUse: boolean
  orgTermsUrl: string
  totalParticipants: number
  hideResultsUntilFinished: boolean
}

export interface PollState {
  state: string
  currentQuestionIndex: number
  questions: PollQuestion[]
  userAnswers: UserAnswers
  results: PollQuestion[]
  allowUnregisteredUsers: boolean
  guestCanVote: boolean
  isAuthenticated: boolean
  hasUserVote: boolean
  isReadOnly: boolean
  votingEnded: boolean
  useTermsOfUse: boolean
  agreedTermsOfUse: boolean
  orgTermsUrl: string
  alert: AlertState | null
  checkedTermsOfUse: boolean
  errors: Record<string, unknown>
  isLoading: boolean
  isSubmitting: boolean
  totalParticipants: number
  moduleName: string
  moduleDescription: string
  hideResultsUntilFinished: boolean
  captcha: string
  refreshCaptcha: number
  captchaEnabled: boolean
  prosopoSiteKey: string
}

export interface PollAction {
  type: string
  payload?: unknown
}
