export interface ChapterParagraph {
  id?: number
  key?: string
  name: string
  text: string
}

export interface Chapter {
  id?: number
  key?: string
  name: string
  paragraphs: ChapterParagraph[]
}

export interface DocumentErrors {
  [key: number]: {
    name?: string[]
    paragraphs?: Array<Record<string, unknown>>
  }
}
