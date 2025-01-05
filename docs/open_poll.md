# Open Poll

It is an enhancement of the existing a4 Poll module, which was accessible only to registered users.  
The open poll allows access to unregister users by a checkbox in the project dashboard poll module. For this enhance feature, we decoupled the creator from the poll's answers and votes. The new class `GeneratedContentModel` - see file [adhocracy4/models/base.py](https://github.com/liqd/adhocracy4/blob/main/adhocracy4/models/base.py) has the creator relation as optional, and introduces the new field/colum `content_id` to provide a unique ID for counting poll's answers and votes in case there is no creator. 

Answers and Votes classes are updated and now they inherit from the new `GeneratedContentModel`. Answer has now as unique together `question`, `creator`, `content_id` depending on whether creator or content_id field exist.

Permissions `allows_unregistered_users` are now also in place for enabling those unregistered users to interact with the open poll in the  - see the file [adhocracy4/polls/predicates.py](https://github.com/liqd/adhocracy4/blob/main/adhocracy4/polls/predicates.py).

For submitting the open poll, we provide a checkbox for `agreed_terms_of_use` of the project same as for registered users at the end of the poll, along with a [captcha written in React](https://github.com/liqd/adhocracy4/blob/main/adhocracy4/static/Captcha.jsx) to filter out robots and spam.

The open poll is intended for public projects only. Private and semi-private projects require a user account to interact with by design, thus the `allow_unregistered_users` has no effect for them. 

At the moment, project insights are not counting unregistered users.
