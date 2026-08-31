import React, { useState } from 'react'

type Idea = {
  pk: number
  name: string
}

type RankedChoiceWidgetProps = {
  moduleId: number
  ideas: Idea[]
  myBallot: number[]
  userCanRank: boolean
  userAuthenticated: boolean
}

function getCsrfToken (): string {
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]*)/)
  return match ? decodeURIComponent(match[1]) : ''
}

async function submitBallot (moduleId: number, ranks: number[]): Promise<boolean> {
  const response = await fetch(`/api/modules/${moduleId}/rankedchoice/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken()
    },
    credentials: 'same-origin',
    body: JSON.stringify({ ranks })
  })
  return response.ok
}

export default function RankedChoiceWidget (props: RankedChoiceWidgetProps) {
  const { moduleId, ideas, myBallot, userCanRank, userAuthenticated } = props
  const [order, setOrder] = useState<number[]>(() => {
    if (myBallot && myBallot.length > 0) {
      return myBallot
    }
    return ideas.map((idea) => idea.pk)
  })
  const [saved, setSaved] = useState<boolean[]>(() => myBallot && myBallot.length > 0 ? Array(myBallot.length).fill(true) : [])
  const [submitting, setSubmitting] = useState(false)
  const [message, setMessage] = useState<string | null>(null)

  const nameOf = (pk: number): string => {
    const idea = ideas.find((i) => i.pk === pk)
    return idea ? idea.name : `#${pk}`
  }

  const move = (index: number, direction: -1 | 1) => {
    if (index + direction < 0 || index + direction >= order.length) {
      return
    }
    const next = [...order]
    const current = next[index]
    next[index] = next[index + direction]
    next[index + direction] = current
    setOrder(next)
  }

  const remove = (index: number) => {
    const next = [...order]
    next.splice(index, 1)
    setOrder(next)
  }

  const submit = async () => {
    if (order.length === 0) {
      setMessage('Please rank at least one idea.')
      return
    }
    setSubmitting(true)
    const ok = await submitBallot(moduleId, order)
    setSubmitting(false)
    setSaved(order.map(() => ok))
    setMessage(ok ? 'Your ranking has been saved.' : 'Saving your ranking failed. Please try again.')
  }

  if (!userCanRank) {
    if (!userAuthenticated) {
      return <p className="ranked-choice__login-note">Log in or register to rank the ideas.</p>
    }
    const savedBallot = myBallot.length > 0 ? myBallot : null
    return (
      <div className="ranked-choice ranked-choice--closed">
        <h2 className="ranked-choice__title">Rank the ideas</h2>
        <p className="ranked-choice__hint">The ranking phase is over. The order can no longer be changed.</p>
        {savedBallot ? (
          <ol className="ranked-choice__list">
            {savedBallot.map((pk, index) => (
              <li className="ranked-choice__item" key={pk}>
                <span className="ranked-choice__position is-saved">{index + 1}</span>
                <span className="ranked-choice__name">{nameOf(pk)}</span>
              </li>
            ))}
          </ol>
        ) : (
          <p className="ranked-choice__empty">You did not participate in the ranking.</p>
        )}
      </div>
    )
  }

  if (order.length === 0) {
    return <p className="ranked-choice__empty">There are no ideas to rank yet.</p>
  }

  return (
    <div className="ranked-choice">
      <h2 className="ranked-choice__title">Rank the ideas</h2>
      <p className="ranked-choice__hint">Order the ideas by your preference. The top of the list is your first choice. You may rank only the ideas you support; all others count as your last choice.</p>
      <ol className="ranked-choice__list">
        {order.map((pk, index) => (
          <li className="ranked-choice__item" key={pk}>
            <span className={`ranked-choice__position${saved[index] ? ' is-saved' : ''}`}>{index + 1}</span>
            <span className="ranked-choice__name">{nameOf(pk)}</span>
            <span className="ranked-choice__actions">
              <button type="button" disabled={index === 0} onClick={() => move(index, -1)} aria-label="Move up">&#8593;</button>
              <button type="button" disabled={index === order.length - 1} onClick={() => move(index, 1)} aria-label="Move down">&#8595;</button>
              <button type="button" onClick={() => remove(index)} aria-label="Remove">&#10005;</button>
            </span>
          </li>
        ))}
      </ol>
      <button type="button" className="btn btn-primary" onClick={submit} disabled={submitting}>
        {submitting ? 'Saving...' : 'Save ranking'}
      </button>
      {message && <p className="ranked-choice__message">{message}</p>}
    </div>
  )
}