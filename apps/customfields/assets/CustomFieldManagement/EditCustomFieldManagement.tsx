import React, { useState, useEffect } from 'react'
import django from 'django'
import cookie from 'js-cookie'

import { alert as Alert } from 'adhocracy4'
import { updateDashboard } from 'adhocracy4/adhocracy4/dashboard/assets/dashboard'

import { EditCustomField } from './EditCustomField'
import type { CustomField, FieldChoice } from './types'

const TRANSLATED = {
  addField: django.gettext('Add Field'),
  save: django.gettext('Save'),
  updated: django.gettext('The custom fields have been updated.'),
  updateFailed: django.gettext(
    'The custom fields could not be updated. Please check the data you entered again.'
  )
}

let maxLocalKey = 0
const getNextLocalKey = () => `local_${maxLocalKey++}`

const createEmptyField = (): CustomField => ({
  label: '',
  type: 'open',
  required: false,
  key: getNextLocalKey(),
  choices: []
})

interface AlertValue {
  type: string
  message: string
}

interface EditCustomFieldManagementProps {
  apiUrl: string
  reloadOnSuccess?: boolean
}

export const EditCustomFieldManagement = (props: EditCustomFieldManagementProps) => {
  const [fields, setFields] = useState<CustomField[]>([])
  const [alert, setAlert] = useState<AlertValue | null>(null)

  useEffect(() => {
    fetch(props.apiUrl)
      .then(response => response.json())
      .then(data => {
        setFields(data.fields || [])
      })
  }, [props.apiUrl])

  const updateField = (index: number, updates: Partial<CustomField>) => {
    setFields(prev => prev.map((field, i) => (
      i === index ? { ...field, ...updates } : field
    )))
  }

  const updateChoice = (fIndex: number, cIndex: number, updates: Partial<FieldChoice>) => {
    setFields(prev => prev.map((field, i) => {
      if (i !== fIndex) return field
      const choices = field.choices.map((choice, j) => (
        j === cIndex ? { ...choice, ...updates } : choice
      ))
      return { ...field, choices }
    }))
  }

  const handleFieldAppend = () => {
    setFields(prev => [...prev, createEmptyField()])
  }

  const handleFieldDelete = (index: number) => {
    setFields(prev => prev.filter((_, i) => i !== index))
  }

  const handleTypeChange = (index: number, type: 'choice' | 'open') => {
    setFields(prev => prev.map((field, i) => {
      if (i !== index) return field
      if (type === 'choice' && (!field.choices || field.choices.length === 0)) {
        return {
          ...field,
          type,
          choices: [{ label: '', key: getNextLocalKey() }]
        }
      }
      return { ...field, type }
    }))
  }

  const handleChoiceDelete = (fIndex: number, cIndex: number) => {
    setFields(prev => prev.map((field, i) => {
      if (i !== fIndex) return field
      return {
        ...field,
        choices: field.choices.filter((_, j) => j !== cIndex)
      }
    }))
  }

  const handleChoiceAppend = (fIndex: number) => {
    setFields(prev => prev.map((field, i) => {
      if (i !== fIndex) return field
      return {
        ...field,
        choices: [...field.choices, { label: '', key: getNextLocalKey() }]
      }
    }))
  }

  const clearAlert = () => setAlert(null)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const payload = {
      fields: fields.map(field => {
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        const { key, ...clean } = field
        return clean
      })
    }

    fetch(props.apiUrl, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'X-CSRFToken': cookie.get('csrftoken') || ''
      },
      body: JSON.stringify(payload)
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('update failed')
        }
        return response.json()
      })
      .then(data => {
        setFields(data.fields || [])
        setAlert({ type: 'success', message: TRANSLATED.updated })
        if (props.reloadOnSuccess) updateDashboard()
      })
      .catch(() => {
        setAlert({ type: 'danger', message: TRANSLATED.updateFailed })
      })
  }

  return (
    <form onSubmit={handleSubmit} onChange={clearAlert} className="editpoll__questions custom-fields">

      {fields.map((field, index) => (
        <EditCustomField
          key={field.id || field.key}
          id={field.id || field.key || index}
          field={field}
          title={field.id
            ? django.interpolate(django.gettext('Field %(number)s'), { number: index + 1 }, true)
            : django.gettext('New field')}
          onLabelChange={(label) => updateField(index, { label })}
          onRequiredChange={(required) => updateField(index, { required })}
          onTypeChange={(type) => handleTypeChange(index, type)}
          onChoiceLabelChange={(cIndex, label) => updateChoice(index, cIndex, { label })}
          onDeleteChoice={(cIndex) => handleChoiceDelete(index, cIndex)}
          onAppendChoice={() => handleChoiceAppend(index)}
          onDelete={() => handleFieldDelete(index)}
        />
      ))}

      <Alert onClick={clearAlert} {...alert} />

      <div className="custom-fields__actions">
        <button type="button" className="btn btn--secondary" onClick={handleFieldAppend}>
          <i className="fa fa-plus" aria-hidden="true" />
          {TRANSLATED.addField}
        </button>
        <button type="submit" className="btn btn--primary">
          {TRANSLATED.save}
        </button>
      </div>
    </form>
  )
}
