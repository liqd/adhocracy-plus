import React from 'react'
import { createRoot } from 'react-dom/client'
import PropTypes from 'prop-types'

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
    const languagecode = e.target.textContent
    this.setState({ activeTab: languagecode })
    e.preventDefault()
  }

  addLanguage (e) {
    const languagecode = e.target.getAttribute('languagecode')
    const index = this.state.activeLanguages.indexOf(languagecode)
    const newActiveLanguages = this.state.activeLanguages.concat([])
    if (index === -1) {
      // adding language
      newActiveLanguages.push(languagecode)
    }
    this.setState({
      activeLanguages: newActiveLanguages,
      activeTab: languagecode
    })
  }

  removeLanguage (e) {
    const languagecode = e.target.getAttribute('languagecode')
    const index = this.state.activeLanguages.indexOf(languagecode)
    const newActiveLanguages = this.state.activeLanguages.concat([])
    if (index !== -1) {
      // removing language
      newActiveLanguages.splice(index, 1)
    }
    this.setState({
      activeLanguages: newActiveLanguages
    })
    if (this.state.activeTab === languagecode) {
      this.setState({
        activeTab: this.getNewActiveTab(languagecode)
      })
    }
  }

  render () {
    return (
      <div className="language-choice-container">
        <ul className="checkbox-list nav btn--group">
          {
            this.props.languages.map((languagecode, i) => {
              return (
                <li key={languagecode} className={'nav-item ' + languagecode === this.state.activeTab ? 'active' : ''}>
                  <input
                    type="checkbox" name={languagecode} id={languagecode + '_language-choice'} value={languagecode}
                    checked={this.state.activeLanguages.indexOf(languagecode) !== -1} readOnly
                  />
                  <button
                    href={'#' + languagecode + '_language_panel'} className={'btn btn--light btn--small language-choice ' + (languagecode === this.state.activeTab ? 'active' : '')}
                    data-bs-toggle="tab" onClick={this.activateTab.bind(this)}
                  >{languagecode}
                  </button>
                </li>
              )
            })
          }
        </ul>
        <div className="btn--group ms-5">
          <div className="dropdown">
            <button className="dropdown-toggle btn btn--light btn--small" type="button" data-bs-toggle="dropdown">
              <i className="fa fa-plus" />
            </button>
            <div className="dropdown-menu">
              {
                Object.entries(this.props.languageDict).map(([languagecode, languageString]) => {
                  return (
                    <span key={languagecode}>
                      {this.state.activeLanguages.indexOf(languagecode) === -1 &&
                        <button
                          href={'#' + languagecode + '_language_panel'}
                          className="dropdown-item"
                          data-bs-toggle="tab"
                          languagecode={languagecode}
                          onClick={this.addLanguage.bind(this)}
                          key={languagecode}
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
              <button className="dropdown-toggle btn btn--light btn--small" type="button" data-bs-toggle="dropdown">
                <i className="fa fa-minus" />
              </button>
              <div className="dropdown-menu">
                {
                  Object.entries(this.props.languageDict).map(([languagecode, languageString]) => {
                    return (
                      <span key={languagecode}>
                        {this.state.activeLanguages.indexOf(languagecode) !== -1 &&
                          <button
                            href={languagecode === this.state.activeTab ? '#' + this.getNewActiveTab(languagecode) + '_language_panel' : ''}
                            className="dropdown-item"
                            data-bs-toggle="tab"
                            languagecode={languagecode}
                            onClick={this.removeLanguage.bind(this)}
                            key={languagecode}
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
  const root = createRoot(el)
  root.render(
    <React.StrictMode>
      <LanguageChoice languages={languages} activeLanguages={activeLanguages} languageDict={languageDict} />
    </React.StrictMode>
  )
}
