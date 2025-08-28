import { notificationSettingsData } from './notification_data'
import { useCallback, useState } from 'react'

function initializeNotificationState (initialNotifications, showRestricted) {
  return notificationSettingsData.reduce((acc, group) => {
    if (group.restricted && !showRestricted) return acc

    // create an array of states for each notification from the static data
    Object.keys(group.notifications).forEach(key => {
      const notification = group.notifications[key]
      acc[key] = initialNotifications[key]
      // if we have an activity feed name, add it to the state array
      if (notification.activityFeedName) {
        acc[notification.activityFeedName] = initialNotifications[notification.activityFeedName]
      }
    })

    return acc
  }, {})
}

const useNotifications = (initialNotifications, showRestricted) => {
  const [notificationsState, setNotificationsState] = useState(
    initializeNotificationState(initialNotifications, showRestricted)
  )

  const getMasterToggles = useCallback(() => {
    // return the state of each master toggle
    return notificationSettingsData
      // filter out restricted notifications (for moderators)
      .filter((n) => !n.restricted || (n.restricted && showRestricted))
      .map((n) =>
        // go over remaining notifications
        Object.entries(n.notifications).some(
          // check if either the email notification or in-app notification is toggled true
          ([key, value]) => notificationsState[key] || notificationsState[value.activityFeedName]
        )
      )
  }, [notificationsState, showRestricted])

  return {
    notificationsState,
    setNotificationsState,
    masterToggles: getMasterToggles()
  }
}

export default useNotifications
