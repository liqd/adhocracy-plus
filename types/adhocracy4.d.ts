declare module 'adhocracy4' {
  import * as React from 'react'

  export interface AlertProps {
    type?: 'success' | 'danger' | 'warning' | 'info' | string
    message?: React.ReactNode
    onClick?: () => void
  }

  export const alert: React.FC<AlertProps>
  export const errorList: any
  export const formFieldError: any
  export const api: any
  export const config: any
  export const classNames: (...args: any[]) => string
  export const widget: any
  export const dashboard: any
  export const follows: any
  export const maps: any
  export const mapsReact: any
  export const ratings: any
  export const reports: any
  export const selectDropdown: any
  export const comments: any
  export const commentsAsync: any
  export const aiReport: any
  export const FollowButton: React.FC<any>
  export const followStrings: any
  export const buildFollowSuccessAlert: any
  export const AddressSearch: React.FC<any>
  export const SearchAndShowAddress: React.FC<any>
  export const ControlBarSearch: React.FC<any>
  export const ControlBarDropdown: React.FC<any>
}

declare module 'adhocracy4/adhocracy4/static/widget' {
  export function initialise(
    targetName: string,
    widgetName: string,
    callback: (el: HTMLElement) => void
  ): void
}

declare module 'adhocracy4/adhocracy4/polls/static/PollDetail/TextareaWithCounter' {
  import * as React from 'react'
  export interface TextareaWithCounterProps {
    id: number
    value: string
    onChange: (event: React.ChangeEvent<HTMLTextAreaElement>) => void
    disabled?: boolean
    error?: unknown
    label?: string
  }
  export const TextareaWithCounter: React.FC<TextareaWithCounterProps>
}

declare module 'adhocracy4/adhocracy4/polls/static/PollDetail/ConfidentialNotice' {
  import * as React from 'react'
  export const ConfidentialNotice: React.FC
}

declare module 'adhocracy4/adhocracy4/polls/static/PollDetail/QuestionImage' {
  import * as React from 'react'
  export interface QuestionImageProps {
    imageUrl: string
    alt: string
  }
  const QuestionImage: React.FC<QuestionImageProps>
  export default QuestionImage
}

declare module 'adhocracy4/adhocracy4/polls/static/PollDetail/PollOpenQuestion' {
  import * as React from 'react'
  export interface PollOpenQuestionProps {
    allowUnregisteredUsers: boolean
    question: any
    onOpenChange: (questionId: number, value: string) => void
    errors: Record<string, unknown>
    questionImagesEnabled?: boolean
  }
  export const PollOpenQuestion: React.FC<PollOpenQuestionProps>
}

declare module 'adhocracy4/adhocracy4/static/TermsOfUseCheckbox' {
  import * as React from 'react'
  export interface TermsOfUseCheckboxProps {
    id: string
    onChange: (checked: boolean) => void
    orgTermsUrl?: string
  }
  export const TermsOfUseCheckbox: React.FC<TermsOfUseCheckboxProps>
}

declare module 'adhocracy4/adhocracy4/static/Alert' {
  import * as React from 'react'
  export interface AlertProps {
    type?: string
    message?: string
    onClick?: () => void
  }
  const Alert: React.FC<AlertProps>
  export default Alert
}

declare module 'adhocracy4/adhocracy4/static/FormFieldError' {
  import * as React from 'react'
  export interface FormFieldErrorProps {
    id?: string
    error?: unknown
    field: string
  }
  const FormFieldError: React.FC<FormFieldErrorProps>
  export default FormFieldError
}

declare module 'adhocracy4/adhocracy4/static/api' {
  const api: any
  export default api
}

declare module 'adhocracy4/adhocracy4/follows/static/follows/FollowButton' {
  import * as React from 'react'
  export const FollowButton: React.FC<any>
  export const followStrings: any
  export const buildFollowSuccessAlert: any
  export const updateFollowState: any
}

declare module 'adhocracy4/adhocracy4/dashboard/assets/dashboard' {
  export const updateDashboard: () => void
  export default { updateDashboard: () => void 0 }
}
