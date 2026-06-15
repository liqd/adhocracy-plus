import React from 'react'
import django from 'django'

const ProgressBar = ({ answered, total }) => {
  const percentage = total > 0 ? (answered / total) * 100 : 0
  const rounded = Math.round(percentage)

  return (
    <div className="poll-progress">
      <div className="poll-progress__header">
        <span className="poll-progress__text">
          {django.interpolate(
            django.ngettext(
              '%(answered)s of %(total)s question answered',
              '%(answered)s of %(total)s questions answered',
              total
            ),
            { answered, total },
            true
          )}
        </span>
        <span className="poll-progress__percentage">{rounded}%</span>
      </div>
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
    </div>
  )
}

export default ProgressBar
