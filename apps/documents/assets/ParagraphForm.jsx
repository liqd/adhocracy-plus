const React = require('react')
const django = require('django')
const FormFieldError = require('adhocracy4/adhocracy4/static/FormFieldError')

const ckGet = function (id) {
  return window.CKEDITOR.instances[id]
}

const ckReplace = function (id, config) {
  return window.CKEDITOR.replace(id, config)
}

// translations
const translations = {
  headline: django.gettext('Headline'),
  paragraph: django.gettext('Paragraph'),
  moveUp: django.gettext('Move up'),
  moveDown: django.gettext('Move down'),
  delete: django.gettext('Delete'),
  helpText: django.gettext(
    'If you add an image, please provide an ' +
      'alternate text. It serves as a textual description of the image ' +
      'content and is read out by screen readers. Describe the image in ' +
      'approx. 80 characters. Example: A busy square with people in summer.'
  )
}

class ParagraphForm extends React.Component {
  handleNameChange (e) {
    const name = e.target.value
    this.props.onNameChange(name)
  }

  ckId () {
    return 'id_paragraphs-' + this.props.id + '-text'
  }

  ckEditorDestroy () {
    const editor = ckGet(this.ckId())
    if (editor) {
      editor.destroy()
    }
  }

  ckEditorCreate () {
    if (!ckGet(this.ckId())) {
      const editor = ckReplace(this.ckId(), this.props.config)
      editor.on('change', function (e) {
        const text = e.editor.getData()
        this.props.onTextChange(text)
      }.bind(this))
      editor.setData(this.props.paragraph.text)
    }
  }

  UNSAFE_componentWillUpdate (nextProps) {
    if (nextProps.index > this.props.index) {
      this.ckEditorDestroy()
    }
  }

  componentDidUpdate (prevProps) {
    if (this.props.index > prevProps.index) {
      this.ckEditorCreate()
    }
  }

  componentDidMount () {
    this.ckEditorCreate()
  }

  componentWillUnmount () {
    this.ckEditorDestroy()
  }

  render () {
    const ckEditorToolbarsHeight = 60 // measured on example editor
    return (
      <section className="commenting">
        <div className="commenting__content">
          <div className="commenting__content--border">
            <div className="form-group">
              <label
                htmlFor={'id_paragraphs-' + this.props.id + '-name'}
              >
                {translations.headline}
                <input
                  className="form-control"
                  id={'id_paragraphs-' + this.props.id + '-name'}
                  name={'paragraphs-' + this.props.id + '-name'}
                  type="text"
                  value={this.props.paragraph.name}
                  onChange={this.handleNameChange.bind(this)}
                />
              </label>
              <FormFieldError id={'id_error-' + this.props.id} error={this.props.errors} field="name" />
            </div>

            <div className="form-group">
              <label htmlFor={'id_paragraphs-' + props.id + '-text'}>
                {translations.paragraph}
                <div
                  id={'id_paragraph-help-text-' + props.id}
                  className="form-hint"
                >
                  {translations.helpText}
                </div>
                <div
                  className="django-ckeditor-widget"
                <div
                  id={'id_paragraph-help-text-' + props.id}
                  className="form-hint"
                  data-field-id={'id_paragraphs-' + this.props.id + '-text'}
                  style={{ display: 'inline-block' }}
                >
                  <textarea
                    // fix height to avoid jumping on ckeditor initalization
                    style={{ height: this.props.config.height + ckEditorToolbarsHeight }}
                    id={'id_paragraphs-' + this.props.id + '-text'}
                  />
                </div>
              </label>
              <FormFieldError id={'id_error-' + this.props.id} error={this.props.errors} field="text" />
            </div>
          </div>
        </div>
        <div className="commenting__actions btn-group" role="group">
          <button
            className="btn btn--light btn--small"
            onClick={this.props.onMoveUp}
            disabled={!this.props.onMoveUp}
            title={translations.moveUp}
            type="button"
          >
            <i
              className="fa fa-chevron-up"
              aria-label={translations.moveUp}
            />
          </button>
          <button
            className="btn btn--light btn--small"
            onClick={this.props.onMoveDown}
            disabled={!this.props.onMoveDown}
            title={translations.moveDown}
            type="button"
          >
            <i
              className="fa fa-chevron-down"
              aria-label={translations.moveDown}
            />
          </button>
          <button
            className="btn btn--light btn--small"
            onClick={this.props.onDelete}
            title={translations.delete}
            type="button"
          >
            <i
              className="far fa-trash-alt"
              aria-label={translations.delete}
            />
          </button>
        </div>
      </section>
    )
  }
}

module.exports = ParagraphForm
