import React, { useCallback, useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import { createRoot } from 'react-dom/client'
import django from 'django'
import { FollowButton } from 'adhocracy4'
import { followStrings } from 'adhocracy4/adhocracy4/follows/static/follows/FollowButton'

const ALERT_TARGET = 'project-detail-main'
const ACTIONS_TARGET = 'project-detail-follow-actions'
const AVATARS_TARGET = 'project-detail-followers-avatars'
const LABEL_TARGET = 'project-detail-followers-label'

interface Follower {
  pk: number
  avatar?: string
  avatarFallback?: string
}

function prependFollower (followers: Follower[], user: Follower) {
  return [user, ...followers.filter((f) => f.pk !== user.pk)].slice(0, 4)
}

function removeFollower (followers: Follower[], userPk: number) {
  return followers.filter((f) => f.pk !== userPk)
}

interface FollowerAvatarsProps {
  followers: Follower[]
  following: boolean
  authenticatedAs: boolean | null
  onPlusClick: () => void
}

function FollowerAvatars ({ followers, following, authenticatedAs, onPlusClick }: FollowerAvatarsProps) {
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
            aria-label={followStrings.follow}
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

interface ProjectDetailFollowProps {
  project: unknown
  authenticatedAs: boolean | null
  user?: Follower | null
  initialFollowers?: Follower[]
  initialFollowerCount?: number
}

interface FollowState {
  following: boolean | null
  toggleFollow: () => void
}

function ProjectDetailFollow ({
  project,
  authenticatedAs,
  user,
  initialFollowers,
  initialFollowerCount
}: ProjectDetailFollowProps) {
  const [followers, setFollowers] = useState<Follower[]>(initialFollowers || [])
  const [followerCount, setFollowerCount] = useState(initialFollowerCount || 0)
  const [followState, setFollowState] = useState<FollowState>({
    following: null,
    toggleFollow: () => {}
  })

  const handleFollowChange = useCallback(
    (isFollowing: boolean) => {
      if (!user) return
      setFollowers((current) => {
        const hasUser = current.some((f) => f.pk === user.pk)
        if (isFollowing && !hasUser) {
          setFollowerCount((count) => count + 1)
          return prependFollower(current, user)
        }
        if (!isFollowing && hasUser) {
          setFollowerCount((count) => Math.max(0, count - 1))
          return removeFollower(current, user.pk)
        }
        return current
      })
    },
    [user]
  )

  useEffect(() => {
    const labelEl = document.getElementById(LABEL_TARGET)
    if (!labelEl) return
    const label = django.ngettext(
      '%s Following',
      '%s Following',
      followerCount
    )
    labelEl.textContent = label.replace('%s', String(followerCount))
  }, [followerCount])

  const avatarsEl = document.getElementById(AVATARS_TARGET)

  const handlePlusClick = useCallback(() => {
    followState.toggleFollow()
  }, [followState])

  return (
    <>
      <FollowButton
        project={project}
        authenticatedAs={authenticatedAs}
        alertTarget={ALERT_TARGET}
        buttonTarget={ACTIONS_TARGET}
        customClasses="project-detail__follow"
        buttonClassName="btn btn--light project-detail__follow-btn"
        descriptionId="project-detail-follow-description"
        onFollowChange={handleFollowChange}
        onFollowStateChange={setFollowState}
      />
      {avatarsEl &&
        createPortal(
          <FollowerAvatars
            followers={followers}
            following={followState.following === true}
            authenticatedAs={authenticatedAs}
            onPlusClick={handlePlusClick}
          />,
          avatarsEl
        )}
    </>
  )
}

export function renderProjectDetailFollow (el: HTMLElement) {
  const props = JSON.parse(el.getAttribute('data-attributes') || '{}')
  const root = createRoot(el)
  root.render(<ProjectDetailFollow {...props} />)
}
