import React, { useEffect, useRef, useState } from 'react'
import django from 'django'
import { renderProcaptcha } from '@prosopo/procaptcha-wrapper'

const translated = {
  notArobot: django.gettext('I am not a robot'),
  error: django.gettext('There was a problem loading the CAPTCHA.')
}

interface ProsopoCaptchaProps {
  siteKey?: string
  language?: string
  onChange: (token: string) => void
  name?: string
}

export default function ProsopoCaptcha ({ siteKey, language, onChange, name = 'captcha' }: ProsopoCaptchaProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    if (!containerRef.current) return

    const handleError = () => {
      setError(true)
      onChange('')
    }

    try {
      containerRef.current.innerHTML = ''
      renderProcaptcha(containerRef.current, {
        siteKey,
        language,
        callback: function (token: string) {
          onChange(token)
        },
        'expired-callback': function () {
          onChange('')
        },
        'error-callback': handleError
      } as any)
    } catch {
      queueMicrotask(handleError)
    }
    // only mount once per key/lang
  }, [siteKey, language])

  if (!siteKey || error) {
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
