import React, { useState } from 'react'
import { createRoot } from 'react-dom/client'

interface LanguageChoiceProps {
  activeLanguages: string[]
  languages: string[]
  languageDict: Record<string, string>
}

const LanguageChoice = (props: LanguageChoiceProps) => {
  const [activeLanguages, setActiveLanguages] = useState(props.activeLanguages)
  const [activeTab, setActiveTab] = useState(getInitialActiveTab())

  function getInitialActiveTab () {
    if (props.activeLanguages.length > 0) {
      return props.activeLanguages[0]
    } else {
      return 'de'
    }
  }

  const activateTab = (e: React.MouseEvent<HTMLButtonElement>) => {
    const languagecode = e.currentTarget.textContent || ''
    setActiveTab(languagecode)
    e.preventDefault()
  }

  const addLanguage = (e: React.MouseEvent<HTMLButtonElement>) => {
    const languagecode = e.currentTarget.getAttribute('data-languagecode') || ''
    const index = activeLanguages.indexOf(languagecode)
    const newActiveLanguages = activeLanguages.concat([])
    if (index === -1) {
      // adding language
      newActiveLanguages.push(languagecode)
    }
    setActiveLanguages(newActiveLanguages)
    document.querySelector<HTMLElement>('#' + languagecode)?.click()
  }

  const removeLanguage = (e: React.MouseEvent<HTMLButtonElement>) => {
    const languagecode = e.currentTarget.getAttribute('data-languagecode') || ''
    const index = activeLanguages.indexOf(languagecode)
    const newActiveLanguages = activeLanguages.concat([])
    if (index !== -1) {
      // removing language
      newActiveLanguages.splice(index, 1)
    }
    setActiveLanguages(newActiveLanguages)
    if (activeTab === languagecode) {
      document.querySelector<HTMLElement>('#' + activeLanguages[0])?.click()
    }
  }

  return (
    <div className="language-choice-container">
      <ul className="checkbox-list nav btn--group">
        {
          props.languages.map((languagecode) => {
            const isActive = languagecode === activeTab ? ' active' : ''
            return (
              <li
                key={languagecode}
                className={
                  'nav-item ' + languagecode === activeTab
                    ? 'active'
                    : ''
                }
              >
                <input
                  type="checkbox"
                  name={languagecode}
                  id={languagecode + '_language-choice'}
                  value={languagecode}
                  checked={activeLanguages.indexOf(languagecode) !== -1}
                  readOnly
                />
                <button
                  className={'btn btn--light btn--small language-choice' + isActive}
                  id={languagecode}
                  data-bs-toggle="tab"
                  onClick={activateTab}
                >
                  {languagecode}
                </button>
              </li>
            )
          })
        }
      </ul>
      <div className="btn--group ms-5">
        <div className="dropdown">
          <button
            className="dropdown-toggle btn btn--light btn--small"
            type="button"
            data-bs-toggle="dropdown"
          >
            <i className="fa fa-plus" />
          </button>
          <div className="dropdown-menu">
            {
              Object.entries(props.languageDict).map(([languagecode, languageString]) => {
                return (
                  <span key={languagecode}>
                    {activeLanguages.indexOf(languagecode) === -1 &&
                      <button
                        className="dropdown-item"
                        data-languagecode={languagecode}
                        onClick={addLanguage}
                        key={languagecode}
                      >
                        {languageString}
                      </button>}
                  </span>
                )
              })
            }
          </div>
        </div>

        {activeLanguages.length > 1 &&
          <div className="dropdown">
            <button
              className="dropdown-toggle btn btn--light btn--small"
              type="button"
              data-bs-toggle="dropdown"
            >
              <i className="fa fa-minus" />
            </button>
            <div className="dropdown-menu">
              {
                Object.entries(props.languageDict).map(([languagecode, languageString]) => {
                  return (
                    <span key={languagecode}>
                      {activeLanguages.indexOf(languagecode) !== -1 &&
                        <button
                          className="dropdown-item"
                          data-languagecode={languagecode}
                          onClick={removeLanguage}
                          key={languagecode}
                        >
                          {languageString}
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

export function renderLanguageChoice (el: HTMLElement) {
  const languages = (el.getAttribute('data-languages') || '').split(' ')
  const activeLanguages = (el.getAttribute('data-active-languages') || '').split(' ')
  const languageDict = JSON.parse(el.getAttribute('data-language-dict') || '{}')
  const root = createRoot(el)
  root.render(
    <React.StrictMode>
      <LanguageChoice languages={languages} activeLanguages={activeLanguages} languageDict={languageDict} />
    </React.StrictMode>
  )
}
