adhocracy+ data model
=====================

adhocracy+ is our reference platform based on our software
[adhocracy4](https://github.com/liqd/adhocracy4).

The detailed description of the data model of adhocracy4 can be found
[in the docs](https://github.com/liqd/adhocracy4/blob/master/docs/datamodel.md).
Shortly, there are organisations which can create projects. Projects are made up
of modules, which define which phases are used. The phases determine what the
users are allowed to do.

The definition and descriptions of modules and phases can be found
[here](https://github.com/liqd/adhocracy4/blob/master/docs/phases_and_modules.md).

## Module example in adhocracy+
An example of a module would be the agenda setting. The description and phases
used are defined
[here in the blueprints](https://github.com/liqd/adhocracy-plus/blob/01aa9e1e8139fe5cb6ce887ce33bc548c1dfa63d/apps/dashboard/blueprints.py#L40).
Models, phases and most things needed to make it work are defined in the
[ideas app](https://github.com/liqd/adhocracy-plus/tree/master/apps/ideas). The [model](https://github.com/liqd/adhocracy-plus/blob/master/apps/ideas/models.py)
defines the fields needed to describe the idea and uses ratings and comments
from adhocracy4 as generic relations. To enable the users to rate and comment,
the idea model has to be made
[rateable and commentable in the settings](https://github.com/liqd/adhocracy-plus/blob/92849ba0d8eb5a27c1571f319be0356db8e07347/adhocracy-plus/config/settings/base.py#L373)
and be allowed in the [respective phase](https://github.com/liqd/adhocracy-plus/blob/master/apps/ideas/phases.py).

## Manual and Glossary
To find instructions on the use of a+ as both an initiator and user and
information on the different module types, you can look through our
[adhocracy+ manual](https://manual.adhocracy.plus/:en:start).
