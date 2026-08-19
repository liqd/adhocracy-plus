import React, { useState } from 'react'

interface HoverButtonProps {
  textMouseOn?: string
  textMouseOff: string
  onClick?: () => void
  id?: string
  className?: string
  disabled?: boolean
  icon?: React.ReactNode
}

export const HoverButton = ({
  textMouseOn,
  textMouseOff,
  onClick,
  id,
  className,
  disabled,
  icon
}: HoverButtonProps) => {
  const [prevTextMouseOff, setPrevTextMouseOff] = useState(textMouseOff)
  const [buttonText, setButtonText] = useState(textMouseOff)
  const [processing, setProcessing] = useState(false)

  if (prevTextMouseOff !== textMouseOff) {
    setPrevTextMouseOff(textMouseOff)
    setButtonText(textMouseOff)
    setProcessing(false)
  }

  const handleClick = () => {
    setProcessing(true)
    onClick?.()
  }

  return (
    <button
      id={id}
      className={className}
      type="button"
      onClick={handleClick}
      disabled={processing || disabled}
      onMouseEnter={() => textMouseOn && setButtonText(textMouseOn)}
      onMouseLeave={() => setButtonText(textMouseOff)}
      onFocus={() => textMouseOn && setButtonText(textMouseOn)}
      onBlur={() => setButtonText(textMouseOff)}
      aria-label={buttonText}
    >
      {icon}
      <span className="ms-1">
        {buttonText}
      </span>
    </button>
  )
}
