var PropTypes = require('prop-types')
var React = require('react')
var ReactDOM = require('react-dom')

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
    var index = this.state.activeLanguages.indexOf(removedLanguage)
    var newActiveLanguages = this.state.activeLanguages.concat([])
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
    var languageCode = e.target.textContent
    this.setState({ activeTab: languageCode })
  }

  addLanguage (e) {
    var languageCode = e.target.textContent
    var index = this.state.activeLanguages.indexOf(languageCode)
    var newActiveLanguages = this.state.activeLanguages.concat([])
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
    var languageCode = e.target.textContent
    var index = this.state.activeLanguages.indexOf(languageCode)
    var newActiveLanguages = this.state.activeLanguages.concat([])
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
        <ul className="checkbox-list btn--group" ref="checkboxList">
          {
            this.props.languages.map((languageCode, i) => {
              return (
                <li key={languageCode} className={languageCode === this.state.activeTab ? 'active' : ''}>
                  <input
                    type="checkbox" name={languageCode} id={languageCode + '_language-choice'} value={languageCode}
                    checked={this.state.activeLanguages.indexOf(languageCode) !== -1} readOnly
                  />
                  <a
                    href={'#' + languageCode + '_language_panel'} className={'btn btn--light btn--small language-choice ' + (languageCode === this.state.activeTab ? 'active' : '')}
                    data-toggle="tab" onClick={this.activateTab.bind(this)}
                  >{languageCode}
                  </a>
                </li>
              )
            })
          }
        </ul>
        <div className="btn--group ml-5">
          <div className="dropdown">
            <button className="dropdown-toggle btn btn--light btn--small" type="button" data-toggle="dropdown" ref="toggleButton">
              <i className="fa fa-plus" />
            </button>
            <div className="dropdown-menu">
              {
                this.props.languages.map((languageCode, i) => {
                  return (
                    <span key={languageCode}>
                      {this.state.activeLanguages.indexOf(languageCode) === -1 &&
                        <a
                          href={'#' + languageCode + '_language_panel'} className={'dropdown-item ' + (languageCode === this.state.activeTab ? 'active' : '')}
                          data-toggle="tab"
                          onClick={this.addLanguage.bind(this)}
                          key={languageCode}
                        >{languageCode}
                        </a>}
                    </span>
                  )
                })
              }
            </div>
          </div>

          {this.state.activeLanguages.length > 1 &&
            <div className="dropdown">
              <button className="dropdown-toggle btn btn--light btn--small" type="button" data-toggle="dropdown" ref="toggleButton">
                <i className="fa fa-minus" />
              </button>
              <div className="dropdown-menu">
                {this.state.activeLanguages.map(languageCode => {
                  return (
                    <a
                      href={'#' + this.getNewActiveTab(languageCode) + '_language_panel'}
                      className={'dropdown-item ' + (languageCode === this.getNewActiveTab(languageCode) ? 'active' : '')}
                      data-toggle="tab"
                      onClick={this.removeLanguage.bind(this)}
                      key={languageCode}
                    >{languageCode}
                    </a>
                  )
                })}
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
  ReactDOM.render(
    <LanguageChoice languages={languages} activeLanguages={activeLanguages} />,
    el
  )
}
