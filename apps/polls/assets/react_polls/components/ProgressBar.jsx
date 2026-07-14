import React from 'react'

const ProgressBar = ({ current, total }) => {
  const getLabel = () => {
    if (total <= 1) return ''
    return `${current}/${total}`
  }

  const getPercentage = () => {
    if (total <= 1) return 50
    return 5 + ((current - 1) / (total - 1)) * 90
  }

  const percentage = getPercentage()
  const rounded = Math.round(percentage)
  const label = getLabel()

  return (
    <div className="poll-progress">
      <div className="poll-progress__track">
        <div
          className="poll-progress__bar"
          role="progressbar"
          style={{ width: `${percentage}%` }}
          aria-valuenow={rounded}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
      {label && <div className="poll-progress__label">{label}</div>}
    </div>
  )
}

export default ProgressBar
