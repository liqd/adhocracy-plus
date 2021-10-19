# Django shell basics

To start the django shell, first activate your virtual environment, which
should be installed inside your project folder

`source venv/bin/activate`

If you are working on a server, which was set up as described in the [installation docs](https://github.com/liqd/adhocracy-plus/blob/main/docs/installation_prod.md), the virtualenv is started with

`su aplus`

`cd ~/adhocracy-plus`

`workon aplus`

or in other environments you might need to specify the path to where your python is installed.

Then start the django shell

`python manage.py shell`

## Importing models

You can access objects of your models by first importing the model and then accessing the objects
that are stored in your database. For instance to get all projects (the project model is imported
from adhocrady4), do

`from adhocracy4.projects.models import Project`

`Project.objects.all()`

## Retrieving objects and manipulating them
To get a specific project, you can get it by the id of the project, as this is the primary key

`project = Project.objects.get(id=$myProjectId)`

You could also get it by the name of the project, but since the name is not unique, this might raise an error
if there are several projects with the same name. To do so, type

`project = Project.objects.get(name=$myProjectName)`

You can then access all model fields of your objects, e.g. to get the name of the project, type

`project.name`

If the field you are accessing is an object itself, you can then access this object. For instance to get
the project name of an idea, do

`from apps.ideas.models import Idea`

`idea = Idea.objects.first()`

This gives you the first idea. Ideas have the field module and a module belongs to project.
Thus you get the project name by

`idea.module.project.name`

You can also change the values of fields, e.g. to change the name of a project do

`project.name = 'my new project name'`

`project.save()`

You can also call any method that is defined on the model, e.g. to get the url of you project

`project.get_absolute_url()`

To see all available fields and methods on your project, type:

`dir(project)`


## Filtering

You can filter the objects of your model by specific characteristics, e.g. you could filter all ideas that belong
to the same project:

`project_ideas = Idea.objects.filter(module__project=project)`

project_ideas is a queryset, to see all objects it contatins, type

`project_ideas.all()`

You can also loop through a queryset. To print the names of you project_ideas queryset, do

`for idea in project_ideas.all(): print(idea.name)`
