import React from 'react'
import django from 'django'

const loading = django.gettext('loading')

export default function Spinner () {
  return (
    <div className="align--center">
      <svg className="spinner-land" viewBox="0 0 50 50" aria-label={loading}>
        <circle className="stroke" />
      </svg>
    </div>
  )
}
