import React from 'react'
import { classNames } from 'adhocracy4'

export const ToggleSwitch = ({
  onSwitchStr,
  uniqueId,
  toggleSwitch,
  defaultChecked,
  checked,
  className,
  labelLeft = true,
  size = 'large'
}) => (
  <div className={classNames('toggle-switch form-check', className)}>
    {labelLeft && <label className="toggle-switch__label" htmlFor={uniqueId}>{onSwitchStr}</label>}
    <input
      type="checkbox"
      name={uniqueId}
      id={uniqueId}
      className="toggle-switch__input"
      onChange={toggleSwitch}
      defaultChecked={defaultChecked}
      checked={checked}
    />
    <span className={classNames('toggle-switch__display', size === 'small' && 'toggle-switch__display--small')} hidden>
      <i className="bicon bicon-check toggle-switch__icon toggle-switch__icon--on" aria-hidden="true" />
      <i className="bicon bicon-times toggle-switch__icon toggle-switch__icon--off" aria-hidden="true" />
    </span>
    {!labelLeft && <label className={classNames('toggle-switch__label', size !== 'small' && 'toggle-switch__label--right', size === 'small' && 'toggle-switch__label--small')} htmlFor={uniqueId}>{onSwitchStr}</label>}
  </div>
)
