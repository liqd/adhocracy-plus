# Welcome to Adhocracy+

adhocracy+ is designed to make online participation easy and accessible to everyone. It can be used on our SaaS-platform or installed on your own servers. How to get started on our platform is explained [here](https://adhocracy.plus/info/start/).

*ongoing revision*

## Features of our software
#### [Activity Thread](#activity)
#### [Blueprints/Modules/Templates: Predefined participation modules that can be combined in a project]()

#### [Comments: Comments are an essential part of our platforms as they allow online discussions and debates]()
#### [Community management: Via django (admins) or via frontend (moderators)]()
#### [Dashboard (Initiator Interface)]()
#### [Decision Support Tool: A System that helps to setup a participation process]()
#### [Follow-System: Users can follow projects or other items on our platform.]()
#### [Internationalisation: How to deal with different languages and/or different timzones]()
#### [Login]()
#### [Mailings: All administrative mailings, invitations, notifications, newsletters, platform-mail]()
#### [Moderations Interface]()
#### [Private Projects](#private-projects)
#### [Timelines](#timelines)
#### [User Profile]()
#### [User Permissions]()
#### [Sessions & Tokens for Log-In & Voting]()


## <a name="activity">Activity Thread</a>
there is a table in which each creation, changing and deletion of a configured item is saved, also the project is saved
table can be filtered by project or user and be displayed on userprofile or projectpage

## <a name="private-projects">Private Projects</a>
 When setting up a project it is possible to make this project 'private'. This means not all user on the platform can participate in the project but only the ones that have been added by the project moderators.

There are two concepts on how to access a private projects:

> Moderators invite users via email. Private projects are not shown in any projects overviews at all or only to the ones that have been invited and accepted the invitation
Private Projects are visible within project overviews. When a user that has not been added to the project accesses the project he/she can't see the content of the project but instead a button that allows him/her to request membership


## <a name="timelines">Timelines</a>
*Phase-Timelines*

A participation project can consist of one or more participation modules. Each participation module can consist of one or more phases. Phases define what a user is allowed to do within a certain timeframe, e.g. within an Idea Challenge(→ Participation Module)users can first hand in their ideas (Phase 1) and then - as soon as the second phase starts - rate on the ideas that have been handed in. Phases have to run after one another (so, no simultaneous phases are allowed). So if there are more then one phases inside a module it makes sense to display a timeline, that tells users what they are allowed to do at the moment and in the future.
