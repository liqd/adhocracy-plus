const PropTypes = require('prop-types')
const React = require('react')
const ReactDOM = require('react-dom')

class LanguageChoice extends React.Component {
  constructor (props) {
    super(props)
    this.state = {
      activeLanguages: this.props.activeLanguages,
      activeTab: this.getInitialActiveTab()
    }
  }

  getInitialActiveTab () {
    if (this.props.activeLanguages.length > 0) {
      return this.props.activeLanguages[0]
    } else {
      return 'de'
    }
  }

  getNewActiveTab (removedLanguage) {
    const index = this.state.activeLanguages.indexOf(removedLanguage)
    const newActiveLanguages = this.state.activeLanguages.concat([])
    if (index !== -1) {
      newActiveLanguages.splice(index, 1)
    }
    if (newActiveLanguages.length > 0) {
      return newActiveLanguages[0]
    } else {
      return ''
    }
  }

  activateTab (e) {
    const languageCode = e.target.textContent
    this.setState({ activeTab: languageCode })
  }

  addLanguage (e) {
    const languageCode = e.target.getAttribute('languageCode')
    const index = this.state.activeLanguages.indexOf(languageCode)
    const newActiveLanguages = this.state.activeLanguages.concat([])
    if (index === -1) {
      // adding language
      newActiveLanguages.push(languageCode)
    }
    this.setState({
      activeLanguages: newActiveLanguages,
      activeTab: languageCode
    })
  }

  removeLanguage (e) {
    const languageCode = e.target.getAttribute('languageCode')
    const index = this.state.activeLanguages.indexOf(languageCode)
    const newActiveLanguages = this.state.activeLanguages.concat([])
    if (index !== -1) {
      // removing language
      newActiveLanguages.splice(index, 1)
    }
    this.setState({
      activeLanguages: newActiveLanguages
    })
    if (this.state.activeTab === languageCode) {
      this.setState({
        activeTab: this.getNewActiveTab(languageCode)
      })
    }
  }

  render () {
    return (
      <div className="language-choice-container">
        <ul className="checkbox-list btn--group">
          {
            this.props.languages.map((languageCode, i) => {
              return (
                <li key={languageCode} className={languageCode === this.state.activeTab ? 'active' : ''}>
                  <input
                    type="checkbox" name={languageCode} id={languageCode + '_language-choice'} value={languageCode}
                    checked={this.state.activeLanguages.indexOf(languageCode) !== -1} readOnly
                  />
                  <button
                    href={'#' + languageCode + '_language_panel'} className={'btn btn--light btn--small language-choice ' + (languageCode === this.state.activeTab ? 'active' : '')}
                    data-toggle="tab" onClick={this.activateTab.bind(this)}
                  >{languageCode}
                  </button>
                </li>
              )
            })
          }
        </ul>
        <div className="btn--group ml-5">
          <div className="dropdown">
            <button className="dropdown-toggle btn btn--light btn--small" type="button" data-toggle="dropdown">
              <i className="fa fa-plus" />
            </button>
            <div className="dropdown-menu">
              {
                Object.entries(this.props.languageDict).map(([languageCode, languageString]) => {
                  return (
                    <span key={languageCode}>
                      {this.state.activeLanguages.indexOf(languageCode) === -1 &&
                        <button
                          href={'#' + languageCode + '_language_panel'}
                          className="dropdown-item"
                          data-toggle="tab"
                          languageCode={languageCode}
                          onClick={this.addLanguage.bind(this)}
                          key={languageCode}
                        >{languageString}
                        </button>}
                    </span>
                  )
                })
              }
            </div>
          </div>

          {this.state.activeLanguages.length > 1 &&
            <div className="dropdown">
              <button className="dropdown-toggle btn btn--light btn--small" type="button" data-toggle="dropdown">
                <i className="fa fa-minus" />
              </button>
              <div className="dropdown-menu">
                {
                  Object.entries(this.props.languageDict).map(([languageCode, languageString]) => {
                    return (
                      <span key={languageCode}>
                        {this.state.activeLanguages.indexOf(languageCode) !== -1 &&
                          <button
                            href={languageCode === this.state.activeTab ? '#' + this.getNewActiveTab(languageCode) + '_language_panel' : ''}
                            className="dropdown-item"
                            data-toggle="tab"
                            languageCode={languageCode}
                            onClick={this.removeLanguage.bind(this)}
                            key={languageCode}
                          >{languageString}
                          </button>}
                      </span>
                    )
                  })
                }
              </div>
            </div>}
        </div>
      </div>
    )
  }
}

LanguageChoice.propTypes = {
  activeLanguages: PropTypes.arrayOf(PropTypes.string)
}

module.exports.renderLanguageChoice = function (el) {
  const languages = el.getAttribute('data-languages').split(' ')
  const activeLanguages = el.getAttribute('data-active-languages').split(' ')
  const languageDict = JSON.parse(el.getAttribute('data-language-dict'))
  ReactDOM.render(
    <LanguageChoice languages={languages} activeLanguages={activeLanguages} languageDict={languageDict} />,
    el
  )
}
