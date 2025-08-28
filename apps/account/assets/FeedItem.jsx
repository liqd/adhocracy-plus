import React from 'react'
import django from 'django'
import { classNames } from 'adhocracy4'
import ImageWithPlaceholder from './contrib/ImageWithPlaceholder'

const translations = {
  nowText: django.gettext('now'),
  minutesAgoText: (minutes) =>
    django.interpolate(
      django.gettext('%(minutes)sm ago'),
      { minutes },
      true
    ),
  hoursAgoText: (hours) =>
    django.interpolate(
      django.gettext('%(hours)sh ago'),
      { hours },
      true
    ),
  yesterdayText: django.gettext('Yesterday')
}

export default function FeedItem ({ id, apiUrl, icon, title, thumbnail, body, meta = [], link, linkText, isRead, timestamp, onClickReadLink }) {
  const handleMarkAsRead = async (e) => {
    if (!isRead) {
      e.preventDefault()
      onClickReadLink(id, link, apiUrl)
    }
  }

  return (
    <article className={classNames('feed-item', !isRead && 'feed-item--unread')}>
      <div className="feed-item__icon">
        <i
          className={classNames(
            'fa-solid',
            icon === 'comment' && 'fa-comment',
            icon === 'clock' && 'fa-clock',
            icon === 'heart' && 'fa-heart'
          )}
        />
        {!isRead && <span className="feed-item__unread" />}
      </div>
      <div className="feed-item__content">
        <div className="feed-item__info">
          <div>
            <h3 className={classNames('feed-item__title', isRead && 'feed-item__title--read')} dangerouslySetInnerHTML={{ __html: title }} />
            {meta.length > 0 && (
              <ul className="feed-item__meta">
                {meta.map((item, index) => (
                  <li key={item + index} className="feed-item__meta-item">{item}</li>
                ))}
              </ul>
            )}
          </div>
          <time
            className="feed-item__date"
            title={new Date(timestamp).toLocaleString()}
            dateTime={new Date(timestamp).toISOString()}
          >
            {formatTimestamp(timestamp)}
          </time>
        </div>
        <div className={classNames('feed-item__panel', (body || thumbnail) && 'feed-item__panel--filled')}>
          <div className="feed-item__panel-text">
            {thumbnail && (
              <ImageWithPlaceholder
                src={thumbnail.url}
                alt={thumbnail.alt}
                height={40}
                width={40}
                className="feed-item__thumbnail"
              />
            )}
            {body && <p className={classNames('feed-item__body', thumbnail && 'feed-item__body--thumbnail')}>{body}</p>}
          </div>
          <a className="feed-item__link" href={link} onClick={handleMarkAsRead}>{linkText}</a>
        </div>
      </div>
    </article>
  )
}

function formatTimestamp (timestamp) {
  const date = new Date(timestamp)
  const now = new Date()

  const diffMs = Math.abs(now - date)
  const minutes = Math.floor(diffMs / (1000 * 60))
  const hours = Math.floor(diffMs / (1000 * 60 * 60))
  const days = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (minutes < 1) return translations.nowText
  if (minutes < 60) return translations.minutesAgoText(minutes)
  if (hours < 24) return translations.hoursAgoText(hours)
  if (days === 1) return translations.yesterdayText

  return date.toLocaleDateString()
}
