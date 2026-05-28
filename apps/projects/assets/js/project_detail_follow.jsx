import React, { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import { createRoot } from 'react-dom/client'
import django from 'django'
import Alert from 'adhocracy4/adhocracy4/static/Alert'
import api from 'adhocracy4/adhocracy4/static/api'
import config from 'adhocracy4/adhocracy4/static/config'

const translated = {
  followDescription: django.gettext(
    'Click to be updated about this project via email.'
  ),
  followingDescription: django.gettext(
    'Click to no longer be updated about this project via email.'
  ),
  followAlert: django.gettext(
    'From now on, we\'ll keep you updated on all changes.<br/>Make sure email notifications are enabled in your %(linkStart)s notification settings%(linkEnd)s'
  ),
  followingAlert: django.gettext('You will no longer be updated via email.'),
  follow: django.gettext('Follow'),
  following: django.gettext('Following')
}

const linkParts = {
  linkStart: '<a href="/account/notification-settings/" target="_blank">',
  linkEnd:
    '<i class="fas fa-external-link-alt" role="img" aria-label="Opens in new window"></i></a>'
}

const fullFollowAlertText = django.interpolate(translated.followAlert, linkParts, true)

function prependFollower (followers, user) {
  const withoutUser = followers.filter((f) => f.pk !== user.pk)
  return [user, ...withoutUser].slice(0, 4)
}

function removeFollower (followers, userPk) {
  return followers.filter((f) => f.pk !== userPk)
}

function FollowerAvatars ({ followers, following, authenticatedAs, onPlusClick }) {
  return (
    <ul className="project-detail__avatars">
      {followers.map((follower) => (
        <li className="project-detail__avatar" key={follower.pk}>
          <span
            className="project-detail__avatar-image"
            style={{
              backgroundImage: `url(${follower.avatar || follower.avatarFallback})`
            }}
          />
        </li>
      ))}
      {authenticatedAs && following !== true && (
        <li className="project-detail__avatar project-detail__avatar--more">
          <button
            type="button"
            className="project-detail__avatar-button"
            onClick={onPlusClick}
            aria-pressed={following}
            aria-label={translated.follow}
          >
            <span className="project-detail__avatar-image project-detail__avatar-image--more">
              <i className="fas fa-plus" aria-hidden="true" />
            </span>
          </button>
        </li>
      )}
    </ul>
  )
}

function ProjectDetailFollow ({
  project,
  authenticatedAs,
  alertTarget,
  user,
  initialFollowers,
  initialFollowerCount,
  actionsTarget,
  avatarsTarget,
  labelTarget
}) {
  const [following, setFollowing] = useState(null)
  const [followers, setFollowers] = useState(initialFollowers || [])
  const [followerCount, setFollowerCount] = useState(initialFollowerCount || 0)
  const [alert, setAlert] = useState(null)

  useEffect(() => {
    if (!authenticatedAs) {
      return
    }
    api.follow
      .get(project)
      .done((follow) => {
        setFollowing(follow.enabled)
      })
      .fail((response) => {
        if (response.status === 404) {
          setFollowing(false)
        }
      })
  }, [project, authenticatedAs])

  useEffect(() => {
    if (!labelTarget) { return }
    const labelEl = document.getElementById(labelTarget)
    if (!labelEl) {
      return
    }
    const label = django.ngettext(
      '%s Following',
      '%s Following',
      followerCount
    )
    labelEl.textContent = label.replace('%s', String(followerCount))
  }, [followerCount, labelTarget])

  const removeAlert = () => setAlert(null)

  const toggleFollow = () => {
    if (!authenticatedAs) {
      window.location.href = config.getLoginUrl()
      return
    }

    api.follow.change({ enabled: !following }, project).done((follow) => {
      const isFollowing = follow.enabled
      setFollowing(isFollowing)
      setAlert({
        type: isFollowing ? 'success' : 'warning',
        htmlMessage: isFollowing ? fullFollowAlertText : translated.followingAlert
      })

      if (isFollowing) {
        const alreadyListed = followers.some((f) => f.pk === user.pk)
        if (!alreadyListed) {
          setFollowers((current) => prependFollower(current, user))
          setFollowerCount((count) => count + 1)
        }
      } else {
        const hadUser = followers.some((f) => f.pk === user.pk)
        if (hadUser) {
          setFollowers((current) => removeFollower(current, user.pk))
          setFollowerCount((count) => Math.max(0, count - 1))
        }
      }
    })
  }

  const followBtnText = following ? translated.following : translated.follow
  const followDescriptionText = following
    ? translated.followingDescription
    : translated.followDescription
  const buttonClasses = following
    ? 'a4-btn a4-btn--following project-detail__follow-btn'
    : 'a4-btn a4-btn--follow project-detail__follow-btn'

  const actionsEl = document.getElementById(actionsTarget)
  const avatarsEl = document.getElementById(avatarsTarget)
  const alertEl = alertTarget ? document.getElementById(alertTarget) : null

  return (
    <>
      {actionsEl &&
        createPortal(
          <span className="project-detail__follow">
            <button
              className={buttonClasses}
              type="button"
              onClick={toggleFollow}
              aria-describedby="project-detail-follow-description"
              aria-pressed={following}
              disabled={following === null}
            >
              <span className="a4-follow__btn--content">{followBtnText}</span>
              <span className="a4-sr-only" id="project-detail-follow-description">
                {followDescriptionText}
              </span>
            </button>
          </span>,
          actionsEl
        )}
      {avatarsEl &&
        createPortal(
          <FollowerAvatars
            followers={followers}
            following={following}
            authenticatedAs={authenticatedAs}
            onPlusClick={toggleFollow}
          />,
          avatarsEl
        )}
      {alert && alertEl &&
        createPortal(<Alert onClick={removeAlert} {...alert} />, alertEl)}
    </>
  )
}

export function renderProjectDetailFollow (el) {
  const props = JSON.parse(el.getAttribute('data-attributes'))
  const root = createRoot(el)
  root.render(<ProjectDetailFollow {...props} />)
}
