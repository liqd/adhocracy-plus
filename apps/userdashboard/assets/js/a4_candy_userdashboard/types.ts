export interface ModeratorFeedback {
  pk: number
  feedback_text: string
  last_edit: string
}

export interface ModerationItem {
  pk: number
  item_type: 'comment' | 'idea'
  label: string
  text: string
  title?: string | null
  url: string
  moderate_url: string
  api_url: string
  last_edit: string
  is_modified: boolean
  user_image?: string
  user_name: string
  user_profile_url?: string
  num_reports: number
  is_unread: boolean
  is_blocked: boolean
  is_moderator_marked: boolean
  moderator_feedback?: ModeratorFeedback | null
  feedback_api_url: string
}

export interface FilterItem {
  label: string
  value: string
}
