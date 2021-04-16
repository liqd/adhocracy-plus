import React from 'react'
import django from 'django'

import ModerationComment from './ModerationComment'

export default function (props) {
  const byText = django.pgettext('kosmo', 'By ')

  return (
    <div className="row mb-2">
      <div className="col-12">
        <h1 className="m-0">project title</h1>
        <span className="text-muted">{byText}organisation</span>
        <ModerationComment />
      </div>
    </div>
  )
}
