import React from 'react'

import { ToggleSwitch } from './contrib/ToggleSwitch'
import NotificationToggle from './NotificationToggle'
import { updateItem } from './contrib/helpers'
import { notificationSettingsData } from './notification_data'
import useNotifications from './useNotifications'

const NotificationSettings = ({
  initialNotifications,
  apiUrl,
  showRestricted = false
}) => {
  const {
    notificationsState,
    setNotificationsState,
    masterToggles
  } = useNotifications(initialNotifications, showRestricted)

  const onToggle = (key, force = null) => {
    const newState = { ...notificationsState }
    if (force !== null) newState[key] = force
    else newState[key] = !notificationsState[key]
    setNotificationsState(newState)

    try {
      updateItem({
        [key]: newState[key]
      }, apiUrl, 'PATCH')
    } catch (err) {
      console.error(err)
    }
  }

  const onMasterToggle = (notificationGroup, index) => {
    const newValue = !masterToggles[index]
    const newState = { ...notificationsState }

    Object.keys(notificationGroup.notifications).forEach(key => {
      const notificationSetting = notificationGroup.notifications[key]
      newState[key] = newValue
      if ('activityFeedName' in notificationSetting) {
        newState[notificationSetting.activityFeedName] = newValue
      }
    })

    setNotificationsState(newState)
    try {
      updateItem(newState, apiUrl, 'PATCH')
    } catch (err) {
      console.error(err)
    }
  }

  return (
    <ul className="list--clean">
      {notificationSettingsData.map((notification, index) => {
        if (notification.restricted && !showRestricted) return null

        return (
          <li key={notification.header}>
            <div className="actionable-list__header">
              <h2>{notification.header}</h2>
              <ToggleSwitch
                className="actionable-list__header__action"
                uniqueId={'masterToggle' + index}
                checked={masterToggles[index]}
                toggleSwitch={() => onMasterToggle(notification, index)}
              />
            </div>
            <ul className="actionable-list">
              {Object.entries(notification.notifications).map(([key, value]) => (
                <li key={key} className="actionable-list__item actionable-list__item--hide-last-line">
                  <NotificationToggle
                    name={key}
                    notification={value}
                    notificationState={notificationsState}
                    onToggle={onToggle}
                  />
                </li>
              ))}
            </ul>
          </li>
        )
      })}
    </ul>
  )
}

export default NotificationSettings
