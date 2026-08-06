/* eslint-disable camelcase */
import React, { useState, useEffect } from 'react'
import django from 'django'
import FlipMove from 'react-flip-move'
import update from 'immutability-helper'
import cookie from 'js-cookie'

import { alert as Alert } from 'adhocracy4'
import { updateDashboard } from 'adhocracy4/adhocracy4/dashboard/assets/dashboard'

import { EditCustomField } from './EditCustomField'

const TRANSLATED = {
  addAndEditSectionTitle: django.gettext('Add and Edit Custom Fields'),
  newField: django.gettext('New Field'),
  openQuestion: django.gettext('Open question'),
  multipleChoice: django.gettext('Multiple choice question'),
  save: django.gettext('Save'),
  updated: django.gettext('The custom fields have been updated.'),
  updateFailed: django.gettext(
    'The custom fields could not be updated. Please check the data you entered again.'
  )
}

let maxLocalKey = 0
const getNextLocalKey = () => `local_${maxLocalKey++}`

const createEmptyField = (type) => ({
  label: '',
  type,
  required: false,
  key: getNextLocalKey(),
  choices: type === 'choice' ? [{ label: '', key: getNextLocalKey() }] : []
})

export const EditCustomFieldManagement = (props) => {
  const [fields, setFields] = useState([])
  const [alert, setAlert] = useState(null)

  useEffect(() => {
    fetch(props.apiUrl)
      .then(response => response.json())
      .then(data => {
        setFields(data.fields || [])
      })
  }, [props.apiUrl])

  const updateField = (index, updates) => {
    setFields(update(fields, { [index]: { $merge: updates } }))
  }

  const updateChoice = (fIndex, cIndex, updates) => {
    setFields(update(fields, {
      [fIndex]: { choices: { [cIndex]: { $merge: updates } } }
    }))
  }

  const handleFieldAppend = (type) => {
    setFields([...fields, createEmptyField(type)])
  }

  const handleFieldDelete = (index) => {
    setFields(fields.filter((_, i) => i !== index))
  }

  const handleFieldMove = (index, direction) => {
    const newIndex = index + direction
    if (newIndex < 0 || newIndex >= fields.length) return

    const reordered = [...fields]
    const temp = reordered[index]
    reordered[index] = reordered[newIndex]
    reordered[newIndex] = temp

    setFields(reordered)
  }

  const handleChoiceDelete = (fIndex, cIndex) => {
    const newChoices = fields[fIndex].choices.filter((_, i) => i !== cIndex)
    updateField(fIndex, { choices: newChoices })
  }

  const handleChoiceAppend = (fIndex) => {
    setFields(update(fields, {
      [fIndex]: { choices: { $push: [{ label: '', key: getNextLocalKey() }] } }
    }))
  }

  const clearAlert = () => setAlert(null)

  const handleSubmit = (e) => {
    e.preventDefault()

    const payload = {
      fields: fields.map(field => {
        const { key, ...clean } = field
        return clean
      })
    }

    fetch(props.apiUrl, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'X-CSRFToken': cookie.get('csrftoken')
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
    <form onSubmit={handleSubmit} onChange={clearAlert} className="editpoll__questions">
      <section>
        <h2>{TRANSLATED.addAndEditSectionTitle}</h2>
        <FlipMove easing="cubic-bezier(0.25, 0.5, 0.75, 1)">
          {fields.map((field, index, arr) => {
            const key = field.id || field.key
            return (
              <EditCustomField
                key={key}
                id={key}
                field={field}
                onLabelChange={(label) => updateField(index, { label })}
                onRequiredChange={(required) => updateField(index, { required })}
                onChoiceLabelChange={(cIndex, label) => updateChoice(index, cIndex, { label })}
                onDeleteChoice={(cIndex) => handleChoiceDelete(index, cIndex)}
                onAppendChoice={() => handleChoiceAppend(index)}
                onMoveUp={index > 0 ? () => handleFieldMove(index, -1) : null}
                onMoveDown={index < arr.length - 1 ? () => handleFieldMove(index, 1) : null}
                onDelete={() => handleFieldDelete(index)}
              />
            )
          })}
        </FlipMove>
      </section>

      <Alert onClick={clearAlert} {...alert} />

      <div className="editpoll__question-container">
        <div className="editpoll__question">
          <EditCustomFieldDropdown
            handleAddOpen={() => handleFieldAppend('open')}
            handleAddChoice={() => handleFieldAppend('choice')}
          />
        </div>
        <div className="editpoll__question-actions">
          <button type="submit" className="btn btn--primary">
            {TRANSLATED.save}
          </button>
        </div>
      </div>
    </form>
  )
}

const EditCustomFieldDropdown = ({ handleAddOpen, handleAddChoice }) => (
  <div className="dropdown editpoll__dropdown">
    <button
      type="button"
      className="dropdown-toggle btn btn--light"
      aria-haspopup="true"
      aria-expanded="false"
      data-bs-toggle="dropdown"
    >
      <i className="fa fa-plus" />
      {TRANSLATED.newField}
    </button>
    <div className="dropdown-menu">
      <button
        key="1"
        className="dropdown-item"
        type="button"
        onClick={handleAddChoice}
      >
        {TRANSLATED.multipleChoice}
      </button>
      <button
        key="2"
        className="dropdown-item"
        type="button"
        onClick={handleAddOpen}
      >
        {TRANSLATED.openQuestion}
      </button>
    </div>
  </div>
)
