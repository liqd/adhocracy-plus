# Modules inheritance

Most of a+ participation modules (Idea, Interactive Events, Debate, Documents, Polls, Topics) are inhereted from adhocracy4 [Item model](https://github.com/liqd/adhocracy4/blob/main/adhocracy4/modules/models.py#L418) and the [Moderateable model](https://github.com/liqd/adhocracy-plus/blob/main/apps/moderatorfeedback/models.py#L31).

## Poll module -- aka Survey
![Poll model](assets/poll-inheritance.png)

For the UI interaction see the [wiki diagram](https://wiki.liqd.net/_detail/aplus_poll.png)

## Idea module
![Idea model](assets/idea.png)

For the UI interaction see the [wiki diagram](https://wiki.liqd.net/_detail/aplus_ideachallenge.png)
And the Map Idea module inherits from the AbstractIdea and adds a point field, see the [wiki diagram](https://wiki.liqd.net/_detail/aplus_brainstorming_map.png)

## Topic module
![Topic model](assets/topic.png)

There are two types of topics:  
- Debates: For the UI interaction see the [wiki diagram](https://wiki.liqd.net/_detail/aplus_debate.png)  
- Prioritization: For the UI interaction see the [wiki diagram](https://wiki.liqd.net/_detail/aplus_prioritization.png)

## Text Discussion module
![Chapter model](assets/chapter.png)

For the UI interaction see the [wiki diagram](https://wiki.liqd.net/_detail/aplus_textreview.png)

## Interactive Event module
![Interactive event model](assets/interactive-events.png)

For the UI interaction see the [wiki diagram](https://wiki.liqd.net/_detail/aplus_interactiveevent.png)

## Proposal module -- aka Budgeting
![Budget model](assets/budget.png)

For the UI interaction see the [wiki diagram](https://wiki.liqd.net/_detail/aplus_participatorybudgeting.png)

## Debate module
![Debate model](assets/debate.png)
