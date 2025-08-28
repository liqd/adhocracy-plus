import django from 'django'
import React from 'react'
import { ToggleSwitch } from './contrib/ToggleSwitch'

const emailStr = django.gettext('Email')
const inAppNotificationStr = django.gettext('In-app')

const NotificationToggle = ({ notification, notificationState, name, onToggle }) => {
  const activityFeedName = notification.activityFeedName
  return (
    <>
      <h3>{notification.title}</h3>
      <p>{notification.description}</p>
      <div className="flexbox">
        <ToggleSwitch
          uniqueId={name}
          onSwitchStr={emailStr}
          labelLeft={false}
          checked={notificationState[name]}
          toggleSwitch={() => onToggle(name)}
          size="small"
        />
        {activityFeedName &&
          <ToggleSwitch
            className="ml-1"
            uniqueId={name}
            onSwitchStr={inAppNotificationStr}
            labelLeft={false}
            checked={notificationState[activityFeedName]}
            toggleSwitch={() => onToggle(activityFeedName)}
            size="small"
          />}
      </div>
    </>
  )
}

export default NotificationToggle
