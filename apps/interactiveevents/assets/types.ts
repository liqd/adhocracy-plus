export interface LikeInfo {
  count: number
  session_like: boolean
}

export interface IEQuestion {
  id: number
  text: string
  is_answered: boolean
  is_on_shortlist: boolean
  is_live: boolean
  is_hidden: boolean
  category: string
  likes: LikeInfo
}
