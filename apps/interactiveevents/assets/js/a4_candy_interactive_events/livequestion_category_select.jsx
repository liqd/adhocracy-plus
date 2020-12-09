import django from 'django'
import React from 'react'

export default class SelectCategory extends React.Component {
  componentDidMount () {
    const select = $('#categorySelect')
    select.on('change', this.props.onSelect)
  }

  render () {
    return (
      <div>
        {Object.keys(this.props.category_dict).length > 0 &&
          <div>
            <label className="mb-0" htmlFor="categorySelect">{django.gettext('Affiliation')}*</label>
            <div className="form-hint">
              {django.gettext('Answered questions will be displayed in the statistics according to the chosen affiliation.')}
            </div>
            <div className="row">
              <div className="mb-3 col-md-4 live_questions__select">
                <select
                  name="categorySelect"
                  id="categorySelect"
                  className="js-select2"
                  required="required"
                  data-minimum-results-for-search="Infinity"
                >
                  <option value="">---------</option>
                  {Object.keys(this.props.category_dict).map((categoryPk, index) => {
                    return <option key={index} value={categoryPk}>{this.props.category_dict[categoryPk]}</option>
                  })}
                </select>
              </div>
            </div>
          </div>}
      </div>
    )
  }
}
