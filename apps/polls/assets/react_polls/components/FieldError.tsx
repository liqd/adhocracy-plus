// apps/polls/assets/react_polls/components/FieldError.tsx
import React from 'react'

interface FieldErrorProps {
  id?: string
  error?: unknown
  field: string
}

/**
 * Renders a single field error using the shared "Error Message" form pattern
 * (`.errorlist` with `role="alert"`), so screen readers announce it and the
 * styling matches the rest of the forms.
 */
const FieldError = ({ id, error, field }: FieldErrorProps) => {
  const record = (error ?? {}) as Record<string, unknown>
  const value = record[field]
  if (!value) {
    return null
  }
  const message = Array.isArray(value) ? value[0] : value
  if (!message) {
    return null
  }

  return (
    <ul id={id} className="errorlist" role="alert">
      <li>{String(message)}</li>
    </ul>
  )
}

export default FieldError
