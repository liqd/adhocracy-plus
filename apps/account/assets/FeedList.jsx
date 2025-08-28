import React, { useEffect, useState } from 'react'
import django from 'django'
import Spinner from './contrib/Spinner'
import { alert as Alert } from 'adhocracy4'
import { updateItem } from './contrib/helpers'
import FeedPagination from './FeedPagination'

const translations = {
  errorText: django.gettext('Error'),
  errorNotificationsText: django.gettext('Failed to fetch notifications'),
  markAllAsRead: django.gettext('Mark All As Read')
}

const PAGE_SIZE = 3

export default function FeedList ({ title, description, descriptionNoItems, buttonText, apiUrl, link, renderFeedItem }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [notifications, setNotifications] = useState([])
  const [page, setPage] = useState(1)
  const [totalCount, setTotalCount] = useState(0)
  const [unreadCount, setUnreadCount] = useState(0)

  const totalPages = Math.ceil(totalCount / PAGE_SIZE)

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        setLoading(true)
        setError(null)

        const response = await fetch(
          apiUrl + '?page=' + page + '&page_size=' + PAGE_SIZE
        )

        if (!response.ok) {
          throw new Error(translations.errorNotificationsText)
        }

        const data = await response.json()
        setNotifications(data.results)
        setTotalCount(data.count)
        setUnreadCount(data.unread_count)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchNotifications()
  }, [page])

  const handleMarkAllAsRead = async () => {
    try {
      setError(null)

      const response = await updateItem({ read: true }, apiUrl, 'POST')

      if (!response.ok) {
        throw new Error(translations.errorNotificationsText)
      }

      setUnreadCount(0)
      setNotifications(notifications.map(n => ({ ...n, read: true })))
    } catch (err) {
      setError(err.message)
    }
  }

  const handleMarkAsRead = async (id, link, url) => {
    await updateItem({ read: true }, url + id + '/', 'PUT')
      .then(() => {
        setUnreadCount(unreadCount - 1)
        setNotifications((prevNotifications) =>
          prevNotifications.map((item) =>
            item.id === id ? { ...item, read: true } : item
          )
        )
      })
      .catch((error) => setError(error))
      .finally(() => {
        window.location.href = link
      })
  }

  return (
    <div className="feed-list" aria-live="polite">
      {loading
        ? <Spinner />
        : error
          ? <Alert type="danger" message={translations.errorText + ': ' + error} />
          : (
            <>
              <div className="feed-list__text">
                <div>
                  <h2 className="feed-list__title">
                    {title}{' '}
                    {unreadCount > 0 && (
                      <span className="feed-list__count">{unreadCount}</span>
                    )}
                  </h2>
                  <p className="feed-list__description">
                    {notifications.length > 0 ? description : descriptionNoItems}
                  </p>
                  {notifications.length === 0 && <a className="button" href={link}>{buttonText}</a>}
                </div>
                {unreadCount > 0 && (
                  <div className="feed-list__mark-as-read">
                    <button className="feed-list__mark-as-read-button" onClick={handleMarkAllAsRead}>
                      <i className="fa-solid fa-list-check mr-1" />
                      {translations.markAllAsRead}
                    </button>
                  </div>
                )}
              </div>
              {notifications.length > 0 && (
                <ul className="feed-list__items">
                  {notifications.map((notification, index) => (
                    <li className="feed-list__item" key={notification.id}>
                      {renderFeedItem(notification, index, handleMarkAsRead)}
                    </li>
                  ))}
                </ul>
              )}
              {totalPages > 1 && (
                <FeedPagination
                  page={page}
                  onClickNext={() => setPage(page + 1)}
                  onClickPrevious={() => setPage(page - 1)}
                  onClickPage={(pageNum) => setPage(pageNum)}
                  totalPages={totalPages}
                />
              )}
            </>)}
    </div>
  )
}
