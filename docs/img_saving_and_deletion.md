# Saving and deletion of images  
_conforming to GDPR (General Data Protection Regulation) / DSGVO (Datenschutz-Grundverordnung)_

## General info
All image uploads in the platform, delete previous uploads. E.g when a user uploads a new profile picture, their past picture gets deleted.  
Same for projects, organisations and the modules, the new image will replace the old one.  
Images associated to users and organisations gets deleted when they are deleted. Images uploaded by users for projects and modules are not deleted when a user is deleted, except when the project or the modules are deleted.

## API
The code implementation of the image replacement function is part of Adhocracy4.  
More specifically it happens in the files [images/service.py](https://github.com/liqd/adhocracy4/blob/main/adhocracy4/images/services.py) and [images/signals.py](https://github.com/liqd/adhocracy4/blob/main/adhocracy4/images/signals.py).  
Inside `service.py` the function `delete_images` gets a list of image fields as a function attribute and deletes both the image and the thumbnail of each image field from their respective storage.
The `delete_images` function is called from the `signals.py` file, which defines what object actions (create, save, update, delete an object) should trigger signals.  
The signal `post_save` is triggered when an object (user, project, idea, etc) saves a new image, then the old ones, if any, are deleted (original upload and generated thumbnail) and the new ones are added as a list attribute.  
E.g   
`project.image` and `project.tile_image` 
are added as a list --> `project._a4images_image_fields_current_images` 
which returns a list of the image paths  
The signal `post_init`, which is called every time an object is created, also sets the above attribute for the list of images associated to the object.
Finally, the signal `post_delete` deletes all the images asscociated with the object when the object is deleted.  


## Users
user's image is refered to as `avatar` and it is saved under:
```
       "media/users/images"
```

user avatar gets deleted when their account is deleted via the user dashboard in the browser, which calls the endpoint: 
``` 
accounts.views.AccountDeletionView.form_valid()

account_deletion  # the namespace defined in the accounts.urls.py
```

## Project
Image storage for projects is categorised by date, and a project's two images are saved under:
```
       "media/projects/backgrounds/YYYY/MM/DD"  # decorative background image
       "media/projects/tiles/YYYY/MM/DD"       # project's tile image
```
project images are deleted when its organisation is deleted, and when the project is deleted via the user dashboard in the browser, which calls the endpoint: 
```
projects.views.ProjectDeleteView
project-delete  # the namespace defined in projects.urls.py
```

## Organisation
organisation's two images are saved under:
```
"organisations/logos"
"organisations/backgrounds"  # header image
```
organisation images are deleted when organisation is deleted via django-admin (also this is how an organisation is created).  
When an organisation is deleted, all its related projects with their modules get deleted too.

## Modules

### Idea
Image storage for ideas is categorised by date, and an idea's image is saved under:
```
       "media/ideas/images/YYYY/MM/DD"
```

idea image gets deleted when an idea is deleted via its idea detail page in the browser, which calls the endpoint:
```

ideas.views.IdeaDeleteView  # inherits from AbstractIdeaDeleteView
```

the URI is defined as:

```
idea-delete  # defined in the ideas.urls.py
```

### Budgeting, MapIdea, Topicrio
for those modules, images are deleted when the module is deleted either via the module page or the user dashboard.
Their deletion inherits from the AbstractIdeaDeleteView and their images are also uploaded to:
```
       "media/ideas/images/YYYY/MM/DD"
```

### Budgeting
Module is defined as Proposal and inherits from AbstractMapIdea, thus upload path is defined in the Parent class.
It gets deleted from the budget page in the browser and calls the endpoint:
```
budgeting.views.ProposalDeleteView
proposal-delete  # the namespace defined in the budgeting.urls.py
```

### MapIdea
Module inherits from AbstractIdea, thus upload path is defined in the Parent class.
It gets deleted from the mapidea page in the browser and calls the endpoint:
```
mapideas.views.MapIdeaDeleteView
mapidea-delete  # the namespace defined in the mapideas.urls.py
```

### Topicrio
Module inherits from adhocracy4 Item, thus upload path is defined in the child class and points to `media/ideas/images`.
It gets deleted from the user dashboard and thus it also inherits from adhocracy4.DashboardComponentFormSignalMixin.  
It calls the endpoint:
```
topicrio.views.TopicDeleteView
topic-detail  # the namespace defined in the topicrio.urls.py
```

### Interactive Event
Image is saved under:
```
        "media/interactiveevents/images"
```
Image gets deleted when module is deleted from the user dashboard.


### OfflineEvent
Module inherits from adhocracy4 UserGeneratedContentModel and has no image property.
Images can be uploaded via CKEditor5.

### Debate
Module is defined as Subject class and inherits from adhocracy4 Item and has no image property.

### Document
Module is defined as Chapter class and inherits from adhocracy4 Item. 
It has a one to many relation with Paragraph class, which inherits from adhocracy4 TimeStampedModel.
Paragraph can have images uploaded from CKEditor5.

### Poll
Module inherits from adhocracy4 Item and has no image upload.

### Map
Module inherits from adhocracy4 map fields and has no image upload property.
