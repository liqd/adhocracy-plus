export interface FieldChoice {
  id?: number
  key?: string
  label: string
}

export interface CustomField {
  id?: number
  key?: string
  label: string
  type: 'choice' | 'open'
  required?: boolean
  choices: FieldChoice[]
}
