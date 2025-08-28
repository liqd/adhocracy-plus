import django from 'django'

export const messages = {
  phaseStarted: {
    full: django.gettext('<a href="%(url)s">%(title)s</a> is now open for participation. You can participate until %(date)s'),
    fallback: django.gettext('<a href="%(url)s">%(title)s</a> is now open for participation')
  },
  phaseEnded: {
    full: django.gettext('<a href="%(url)s">%(title)s</a> will end soon. You can still participate until %(date)s'),
    fallback: django.gettext('<a href="%(url)s">%(title)s</a> will end soon')
  },
  offlineEvent: {
    full: django.gettext('The event %(eventName)s in <a href="%(url)s">%(title)s</a> is coming up soon and takes place on %(date)s'),
    fallback: django.gettext('The event %(eventName)s in <a href="%(url)s">%(title)s</a> is coming up soon')
  }
}

// Helper function that handles date validation and message interpolation
const getDateAwareMessage = (fullMessage, fallbackMessage, data) => {
  try {
    if (data.date && !isNaN(new Date(data.date).getTime())) {
      return django.interpolate(fullMessage, data, true)
    }
  } catch (e) {
    // Fall through to fallback message
  }

  const { date, ...fallbackData } = data
  return django.interpolate(fallbackMessage, fallbackData, true)
}

export const notificationsData = {
  interactions: {
    title: django.gettext('Interactions'),
    description: django.gettext(
      'Here you can see all the interactions you have with other users on meinBerlin.'
    ),
    descriptionNoItems: django.gettext(
      'No reactions to your posts yet. Get involved to get reactions.'
    ),
    buttonText: django.gettext('Find participation projects'),
    userSupportedProposal: (title, url) => django.interpolate(
      django.gettext('A user supported your proposal in <a href="%(url)s">%(title)s</a>'),
      { title, url },
      true
    ),
    moderatorRemarkedIdeaText: (title, url) => django.interpolate(
      django.gettext('A moderator has remarked on your idea in <a href="%(url)s">%(title)s</a>'),
      { title, url },
      true
    ),
    moderatorRemarkedProposalText: (title, url) => django.interpolate(
      django.gettext('A moderator has remarked on your proposal in <a href="%(url)s">%(title)s</a>'),
      { title, url },
      true
    ),
    moderatorReplieIdeaText: (title, url) => django.interpolate(
      django.gettext('A moderator has responded to your idea in <a href="%(url)s">%(title)s</a>'),
      { title, url },
      true
    ),
    userRepliedIdeaText: (title, url) => django.interpolate(
      django.gettext('A user has replied to your idea in <a href="%(url)s">%(title)s</a>'),
      { title, url },
      true
    ),
    userRepliedProposalText: (title, url) => django.interpolate(
      django.gettext('A user has replied to your proposal in <a href="%(url)s">%(title)s</a>'),
      { title, url },
      true
    ),
    userRepliedPollText: (title, url) => django.interpolate(
      django.gettext('A user has replied to your poll in <a href="%(url)s">%(title)s</a>'),
      { title, url },
      true
    ),
    moderatorRepliedCommentText: (title, url) => django.interpolate(
      django.gettext('A moderator has responded to your comment in <a href="%(url)s">%(title)s</a>'),
      { title, url },
      true
    ),
    userRepliedCommentText: (title, url) => django.interpolate(
      django.gettext('A user has replied to your comment in <a href="%(url)s">%(title)s</a>'),
      { title, url },
      true
    ),
    usersRatedIdeaText: (title, url) => django.interpolate(
      django.gettext('Users have rated your idea in <a href="%(url)s">%(title)s</a>'),
      { title, url },
      true
    ),
    userRatedIdeaText: (title, url) => django.interpolate(
      django.gettext('A user has rated your idea in <a href="%(url)s">%(title)s</a>'),
      { title, url },
      true
    ),
    usersRatedCommentText: (title, url) => django.interpolate(
      django.gettext('Users have rated your comment in <a href="%(url)s">%(title)s</a>'),
      { title, url },
      true
    ),
    userRatedCommentText: (title, url) => django.interpolate(
      django.gettext('A user has rated your comment in <a href="%(url)s">%(title)s</a>'),
      { title, url },
      true
    )
  },
  searchProfiles: {
    title: django.gettext('Search Profiles'),
    description: django.gettext(
      'Here you will find newly published participation projects that match your search profiles.'
    ),
    descriptionNoItems: django.gettext(
      'No results from your saved searches yet. Add new saved searches and wait for a matching project to be published.'
    ),
    buttonText: django.gettext('Save a search'),
    projectMatchesSearchProfileText: (title, url, name, isProject) => django.interpolate(
      django.gettext('A new %(obj)s, <a href="%(url)s">%(title)s</a>, matches your search profile %(name)s'),
      {
        title,
        url,
        name,
        obj: isProject ? django.gettext('project') : django.gettext('plan')
      },
      true
    )
  },
  followedProjects: {
    title: django.gettext('Followed projects'),
    description: django.gettext(
      'Here you will receive all the latest news about the projects you follow.'
    ),
    descriptionNoItems: django.gettext(
      'No followed projects. Find projects to follow them.'
    ),
    buttonText: django.gettext('Find projects'),
    phaseStartedText: (title, url, date) => getDateAwareMessage(
      messages.phaseStarted.full,
      messages.phaseStarted.fallback,
      { title, url, date }
    ),

    phaseEndedText: (title, url, date) => getDateAwareMessage(
      messages.phaseEnded.full,
      messages.phaseEnded.fallback,
      { title, url, date }
    ),

    offlineEvent: (eventName, title, url, date) => getDateAwareMessage(
      messages.offlineEvent.full,
      messages.offlineEvent.fallback,
      { eventName, title, url, date }
    )
  },
  viewIdeaText: django.gettext('View idea'),
  viewCommentText: django.gettext('View comment'),
  viewProjectText: django.gettext('View project'),
  viewProposalText: django.gettext('View proposal'),
  viewPlanText: django.gettext('View plan')
}

export const notificationSettingsData = [
  {
    header: django.gettext('Project-Related Notifications'),
    notifications: {
      email_newsletter: {
        title: django.gettext('E-Mail Newsletter'),
        description: django.gettext('Receive newsletters with updates and news about the projects you follow via e-mail.')
      },
      notify_followers_phase_started: {
        title: django.gettext('Participation Start'),
        description: django.gettext('Receive a notification when a participation begins in a project you follow.'),
        activityFeedName: 'track_followers_phase_started'
      },
      notify_followers_phase_over_soon: {
        title: django.gettext('Participation End'),
        description: django.gettext('Receive a notification when a participation is near its end in a project you follow.'),
        activityFeedName: 'track_followers_phase_over_soon'
      },
      notify_followers_event_upcoming: {
        title: django.gettext('Event'),
        description: django.gettext('Receive notifications for upcoming events in projects you follow.'),
        activityFeedName: 'track_followers_event_upcoming'
      }
    }
  },
  {
    header: django.gettext('Interactions with other users'),
    notifications: {
      notify_creator: {
        title: django.gettext('Reactions from other users to your posts'),
        description: django.gettext('Receive a notification when someone rates or comments on your post.'),
        activityFeedName: 'track_creator'
      },
      notify_creator_on_moderator_feedback: {
        title: django.gettext('Reactions of moderation'),
        description: django.gettext('Receive a notification for feedback and status changes of your idea from the moderation.'),
        activityFeedName: 'track_creator_on_moderator_feedback'
      }
    }
  },
  {
    header: django.gettext('Notifications for Initiators and Moderators'),
    restricted: true,
    notifications: {
      notify_initiators_project_created: {
        title: django.gettext('New Project in Your Organization'),
        description: django.gettext('Receive a notification when a new project is created in your organization.')
      },
      notify_moderator: {
        title: django.gettext('New Contribution in a Moderated Project'),
        description: django.gettext('Receive a notification when a new contribution is added to a project you moderate.')
      }
    }
  }
]
