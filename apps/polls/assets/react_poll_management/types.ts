// apps/polls/assets/react_poll_management/types.ts

export interface ManagementChoice {
  id?: number
  key: string
  label: string
  is_other_choice: boolean
  count?: number
}

export interface ManagementQuestion {
  id?: number
  key: string
  label: string
  help_text: string
  multiple_choice: boolean
  is_open: boolean
  is_confidential: boolean
  choices: ManagementChoice[]
  answers?: unknown[]
  image_base64?: string | null
  image_url?: string | null
  image_alt_text?: string
  image_help_text?: string
}

export interface ChoiceErrors {
  label?: string[]
}

export interface QuestionErrors {
  label?: string[]
  help_text?: string[]
  is_open?: string[]
  image_base64?: string[]
  image_alt_text?: string[]
  choices?: (ChoiceErrors | null)[]
  [key: string]: string[] | (ChoiceErrors | null)[] | undefined
}

export interface AlertValue {
  type: string
  message: string
}

export interface PollManagementProps {
  pollId: number
  reloadOnSuccess?: boolean
  enableUnregisteredUsers?: boolean
  questionImagesEnabled?: boolean
}
