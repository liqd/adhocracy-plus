import React from 'react'
import QuestionModerator from './QuestionModerator'
import QuestionUser from './QuestionUser'
import type { IEQuestion } from './types'

interface QuestionListProps {
  isModerator: boolean
  hasLikingPermission: boolean
  questions: IEQuestion[]
  removeFromList: (id: number, data: Record<string, number | boolean>) => void
  updateQuestion: (data: Record<string, number | boolean>, id: number) => Promise<Response>
  handleLike: (this: unknown, id: number, value: boolean) => Promise<Response>
  togglePollingPaused: () => void
}

const QuestionList = (props: QuestionListProps) => {
  if (props.isModerator) {
    return (
      <div>
        {
          props.questions.map((question) => {
            return (
              <QuestionModerator
                key={question.id}
                displayIsOnShortlist={!question.is_hidden}
                displayIsLive={!question.is_hidden}
                displayIsHidden
                displayIsAnswered={!question.is_hidden}
                removeFromList={props.removeFromList.bind(this)}
                updateQuestion={props.updateQuestion.bind(this)}
                id={question.id}
                is_answered={question.is_answered}
                is_on_shortlist={question.is_on_shortlist}
                is_live={question.is_live}
                is_hidden={question.is_hidden}
                category={question.category}
                likes={question.likes}
                togglePollingPaused={props.togglePollingPaused}
              >
                {question.text}
              </QuestionModerator>
            )
          })
        }
      </div>
    )
  } else {
    return (
      <div>
        {
          props.questions.map((question) => {
            return (
              <QuestionUser
                key={question.id}
                handleLike={props.handleLike.bind(this)}
                hasLikingPermission={props.hasLikingPermission}
                id={question.id}
                is_on_shortlist={question.is_on_shortlist}
                is_live={question.is_live}
                category={question.category}
                likes={question.likes}
              >
                {question.text}
              </QuestionUser>
            )
          })
        }
      </div>
    )
  }
}

export default QuestionList
