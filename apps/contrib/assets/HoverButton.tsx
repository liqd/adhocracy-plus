import React, { useState, useEffect } from 'react'

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
  const [buttonText, setButtonText] = useState(textMouseOff)
  const [processing, setProcessing] = useState(false)

  const handleClick = () => {
    setProcessing(true)
    onClick?.()
  }

  useEffect(() => {
    // intentionally reset state when the off-state text changes
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setProcessing(false)
    setButtonText(textMouseOff)
  }, [textMouseOff])

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
