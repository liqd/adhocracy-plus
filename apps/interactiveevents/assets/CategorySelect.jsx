import django from 'django'
import React, { useEffect } from 'react'

export const CategorySelect = (props) => {
  useEffect(() => {
    const select = document.getElementById('categorySelect')
    select.addEventListener('change', props.onSelect)
  }, [])

  const affiliationStr = django.gettext('Affiliation')
  const answeredQuestionsStr = django.gettext('Answered questions will be displayed in the statistics according to the chosen affiliation.')

  return (
    <div>
      {Object.keys(props.category_dict).length > 0 &&
        <div>
          <label className="mb-0" htmlFor="categorySelect">{affiliationStr}*</label>
          <div className="form-hint">
            {answeredQuestionsStr}
          </div>
          <div className="row">
            <div className="mb-3 col-md-4 live_questions__select">
              <select
                name="categorySelect"
                id="categorySelect"
                className="form-select"
                required="required"
                data-minimum-results-for-search="Infinity"
              >
                <option value="">---------</option>
                {Object.keys(props.category_dict).map((categoryPk, index) => {
                  return <option key={index} value={categoryPk}>{props.category_dict[categoryPk]}</option>
                })}
              </select>
            </div>
          </div>
        </div>}
    </div>
  )
}
