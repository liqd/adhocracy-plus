import django from 'django'
import React from 'react'
import { updateItem } from './helpers.js'
import CategorySelect from './livequestion_category_select'

export default class QuestionForm extends React.Component {
  constructor (props) {
    super(props)
    this.state = {
      question: '',
      selectedCategory: '',
      questionCharCount: 0
    }
  }

  selectCategory (e) {
    this.setState({ selectedCategory: e.target.value })
  }

  handleTextChange (e) {
    this.setState({
      question: e.target.value,
      questionCharCount: e.target.value.length
    })
  }

  getPrivacyPolicyLabelWithLinks () {
    const splittedLabel = this.props.privatePolicyLabel.split('{}')
    return (
      <span>
        {splittedLabel[0]}
        <a href={this.props.termsOfUseUrl} target="_blank" rel="noreferrer">{splittedLabel[1]}</a>
        {splittedLabel[2]}
        <a href={this.props.dataProtectionPolicyUrl} target="_blank" rel="noreferrer">{splittedLabel[3]}</a>
        {splittedLabel.length > 4 ? splittedLabel[4] : ''}*
      </span>
    )
  }

  addQuestion (e) {
    e.preventDefault()
    const anchor = document.getElementById('question-list-end')
    const url = this.props.questions_api_url
    const data = {
      text: this.state.question,
      category: this.state.selectedCategory
    }
    updateItem(data, url, 'POST')
    this.setState({
      question: '',
      questionCharCount: 0
    })
    anchor.scrollIntoView({ behavior: 'smooth', block: 'end' })
    this.props.restartPolling()
  }

  render () {
    return (
      <div>
        <form id="id-livequestion-form" action="" onSubmit={this.addQuestion.bind(this)}>
          <h2>{django.gettext('Here you can ask your question')}</h2>
          <CategorySelect
            onSelect={this.selectCategory.bind(this)}
            category_dict={this.props.category_dict}
          />
          <label htmlFor="questionTextField">{django.gettext('Question')}*</label>
          <textarea
            placeholder={django.gettext('Add Question')}
            id="questionTextField"
            className="form-control"
            name="questionTextFieldName"
            rows="3"
            onChange={this.handleTextChange.bind(this)}
            required="required"
            value={this.state.question}
            maxLength="1000"
          />
          <label htmlFor="id-livequestion-form" className="live_questions__char-count">{this.state.questionCharCount}/1000{django.gettext(' characters')}</label>
          <div className="form-check">
            <label className="form-check__label">
              <input type="checkbox" name="data_protection" id="data_protection_check" required="required" />
              &nbsp;
              {this.getPrivacyPolicyLabelWithLinks()}
            </label>
          </div>
          <div className="d-flex justify-content-end">
            <input type="submit" value={django.gettext('Add Question')} className="btn" />
          </div>
        </form>
      </div>
    )
  }
}
