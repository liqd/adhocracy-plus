import React, { useState, useEffect } from 'react'

export const HoverButton = (props) => {
  const { textMouseOn, textMouseOff, onClick } = props
  const [buttonText, setButtonText] = useState(textMouseOff)
  const [processing, setProcessing] = useState(false)

  const handleClick = () => {
    setProcessing(true)
    onClick()
  }

  useEffect(() => {
    setProcessing(false)
    setButtonText(textMouseOff)
  }, [textMouseOff])

  return (
    <button
      id={props.id}
      className={props.className}
      type="button"
      onClick={handleClick}
      disabled={processing || props.disabled}
      onMouseEnter={() => setButtonText(textMouseOn)}
      onMouseLeave={() => setButtonText(textMouseOff)}
      onFocus={() => setButtonText(textMouseOn)}
      onBlur={() => setButtonText(textMouseOff)}
      aria-label={buttonText}
    >
      {props.icon}
      <span className="ms-1">
        {buttonText}
      </span>
    </button>
  )
}
