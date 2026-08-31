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
  resultsVisible: boolean
  results: ResultItem[]
}

type ResultItem = {
  place: number
  pk: number
  name: string
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
  const { moduleId, ideas, myBallot, userCanRank, userAuthenticated, resultsVisible, results } = props
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
    return (
      <RankedChoiceTabs
        resultsVisible={resultsVisible}
        results={results}
        myBallot={myBallot}
        userAuthenticated={userAuthenticated}
        nameOf={nameOf}
        defaultTab={resultsVisible ? "results" : "own"}
      />
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

function RankedChoiceTabs (props: {
  resultsVisible: boolean
  results: ResultItem[]
  myBallot: number[]
  userAuthenticated: boolean
  nameOf: (pk: number) => string
  defaultTab: string
}) {
  const { resultsVisible, results, myBallot, userAuthenticated, nameOf, defaultTab } = props
  const [tab, setTab] = useState(defaultTab)
  return (
    <div className="ranked-choice">
      <div className="ranked-choice__tabs">
        {resultsVisible ? (
          <button type="button" className={"ranked-choice__tab" + (tab === "results" ? " is-active" : "")} onClick={() => setTab("results")}>Result</button>
        ) : null}
        <button type="button" className={"ranked-choice__tab" + (tab === "own" ? " is-active" : "")} onClick={() => setTab("own")}>My ranking</button>
      </div>
      {tab === "results" ? (
        <div className="ranked-choice__results">
          {results.length > 0 ? (
            <ol className="ranked-choice__result-list">
              {results.map((item) => (
                <li className="ranked-choice__result-item" key={item.pk}>
                  <span className={"ranked-choice__place" + (item.place === 1 ? " is-first" : item.place === 2 ? " is-second" : item.place === 3 ? " is-third" : "")}>{item.place}</span>
                  <span className="ranked-choice__name">{item.name}</span>
                </li>
              ))}
            </ol>
          ) : (
            <p className="ranked-choice__empty">There are not enough ballots to determine a result yet.</p>
          )}
        </div>
      ) : (
        <div className="ranked-choice__own">
          {!userAuthenticated ? (
            <p className="ranked-choice__login-note">Log in to see your ranking.</p>
          ) : myBallot.length > 0 ? (
            <ol className="ranked-choice__list">
              {myBallot.map((pk, index) => (
                <li className="ranked-choice__item" key={pk}>
                  <span className="ranked-choice__position is-saved">{index + 1}</span>
                  <span className="ranked-choice__name">{nameOf(pk)}</span>
                </li>
              ))}
            </ol>
          ) : (
            <p className="ranked-choice__empty">You did not participate in the ranking.</p>
          )}
          <p className="ranked-choice__hint">The ranking phase is over. The order can no longer be changed.</p>
        </div>
      )}
    </div>
  )
}
