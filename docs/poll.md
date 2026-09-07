# Poll
The poll module (aka Survey) can be attached as a participation type in the project's dashboard. A poll has Questions that users can interact either by giving an Answer in text format, or by voting on Choices. A Vote can also receive another vote and an answer. Therefore the way answers and votes are related to the Poll, is through the Question table. Votes particularly are first related to a choice, which choice is related to a question.

![Poll diagram](assets/poll-question-answer-vote-inheritance.png)
**enlarge the image with right-click**

# Open Poll

It is an enhancement of the existing a4 Poll module, which was accessible only to registered users.  
The open poll allows access to unregister users by a checkbox in the project's dashboard poll module. For this enhanced feature, we decoupled the creator from the poll's answers and votes. The new class `GeneratedContentModel` - see file [adhocracy4/models/base.py](https://github.com/liqd/adhocracy4/blob/main/adhocracy4/models/base.py) has the creator relation as optional, and introduces the new field `content_id` to provide a unique ID for filtering the answers and votes of a non registered user, because there is no creator. 

Answers and Votes classes used to inherit from the `UserGeneratedContentModel` and have been updated to inherit now from the new `GeneratedContentModel`, so they may either have a creator or a content_id field. Answer has also a constrain (unique together) in the combination of `Question`, `Creator`, `Content_id` depending on whether a creator or content_id field exists.

Permissions `allows_unregistered_users` are now also in place for enabling those unregistered users to interact with the open poll - see the file [adhocracy4/polls/predicates.py](https://github.com/liqd/adhocracy4/blob/main/adhocracy4/polls/predicates.py).

For submitting the open poll, we provide a checkbox labelled with `agreed_terms_of_use` which is equivalent to agreement of the project's terms users have to accept upon signing-up. The terms agreement checheckbox is placed at the end of the poll, along with a [captcha written in React](https://github.com/liqd/adhocracy4/blob/main/adhocracy4/static/Captcha.jsx) to filter out robots and spam. Both fields need to filled in by the user in order to be able to submit the poll form.

The open poll is intended for public projects only. Private and semi-private projects require a user account to interact with by design, thus the `allow_unregistered_users` option in the poll module dashboard has no effect for these type of projects. 

Project insights do count unregistered users, and exporting a poll as an excel also counts votes and answers from unregistered users with the prefix 'ANON'.

# Admin moderation of open answers

Open (free-text) answers can be managed in the Django admin under **Polls → Answers**
(`apps/polls/admin.py`). This is an admin-only intervention tool, not a
general moderation feature inside the poll module.

- **List, search, filter:** admins can see all open answers and locate specific
  ones by answer text, creator, project, organisation, question, or date.
- **Edit:** the answer text of an individual open answer can be corrected.
  Creator, content and timestamp fields are read-only.
- **Delete:** a single answer can be deleted. Because answers are stored in
  their own table (independent of choices/votes) and counts are computed
  dynamically, deleting an answer removes it from the result display and from
  exports without affecting the poll's overall counts or "other" votes.
- **Traceability:** every action is recorded via Django's built-in admin history
  (`django.contrib.admin.models.LogEntry`). When an admin edits an answer, the
  change message stores both the previous and the new answer text. The full
  action log is browsable and searchable through the read-only **Admin → Log
  entries** view (by user, content type, action flag, and date).
