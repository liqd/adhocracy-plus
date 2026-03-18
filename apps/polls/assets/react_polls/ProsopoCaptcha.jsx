import React, { useEffect, useRef, useState } from 'react'
import django from 'django'
import { renderProcaptcha } from '@prosopo/procaptcha-wrapper'

const translated = {
  notArobot: django.gettext('I am not a robot'),
  error: django.gettext('There was a problem loading the CAPTCHA.')
}

export default function ProsopoCaptcha ({ siteKey, language, onChange, name = 'captcha' }) {
  const containerRef = useRef(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    if (!siteKey) {
      setError(true)
      return
    }
    if (!containerRef.current) return

    try {
      containerRef.current.innerHTML = ''
      renderProcaptcha(containerRef.current, {
        siteKey,
        language,
        callback: function (token) {
          onChange(token)
        },
        'expired-callback': function () {
          onChange('')
        },
        'error-callback': function () {
          setError(true)
          onChange('')
        }
      })
    } catch (e) {
      setError(true)
      onChange('')
    }
    // only mount once per key/lang
  }, [siteKey, language])

  if (error) {
    return <span className="captcheck_error_message">{translated.error}</span>
  }

  return (
    <div className="u-spacer-bottom">
      <div className="u-spacer-bottom-half">
        <label htmlFor={name}>
          {translated.notArobot}
          <span role="presentation" title="This field is required">*</span>
        </label>
        <input id={name} type="hidden" name={name} value="" />
      </div>
      <div ref={containerRef} className="prosopo-captcha-container" data-site-key={siteKey} />
    </div>
  )
}
