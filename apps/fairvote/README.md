# Fair Vote Module

## Prerequisites:
Database: We're using Mysql

## Requirements:

## Installation
1. Follow the [adhocracy-plus installation guide](https://github.com/ariel-research/adhocracy-plus/README.md).

## Production
1. Run the following commands:
        
        npm run build:prod
        export DJANGO_SETTINGS_MODULE=adhocracy-plus.config.settings.build
        python manage.py compilemessages
        python manage.py collectstatic

2. Restart the service.

## Simulations:
### `create-delete` file:
For initialization:
1. Set the following variables as you want: 
    
        ORG = "org-name"
        PROJECT = "project-name"
        MODULE = "module-name"
        superuser_name = "superuser-name"
        superuser_pass = "superuser-password" 
 
2. Run the following functions:
    1. **create_superuser** - create superuser that will be the organisation inventor.
    2. **create_organisation** - create the organisation in order to add project.
    3. **create_project** - create the project in order to add modules. (use can you the returned organisation for 'org' argument)
    4. **create_module** - create the fairvote module which allows users add ideas and support them. (use can you the returned organisation for 'project' argument)
    5. **register** - register all users in the 'user_list'.

For reset:
1. 

### `simulator_sn`/`simulator_sn_bicycle` file:
**Prerequisites:**
firefox browser

**Required libraries:**
1. mechanize
2. selenium

**For initialization:**
1. Set the following variables as you want: 

        URL = "http://localhost:8004"
        ORG = "org-name"
        PROJECT = "project-name"
        MODULE = "module-name"
        superuser_name = "superuser-name"
        superuser_pass = "password"

2. Ensure that `user_list` equals to the one in the previous file.
3. You can edit the `idea_list` if you want to.
4. Run the following functions:
    ### submit ideas (by superuser)
    1. submit_ideas_simulator()

    ### users vote ideas
    1. `users = user_list.copy()`
    2. `random.shuffle(users)`
    3. `link = f"{URL}/{ORG}/projects/module/{MODULE}/?"` - module url
    5. `ideas_p = get_all_ideas(link)` - idea links list
    6. `vote_ideas_simulator(ideas_p)` - the voting simulator

    ### Accepting ideas by superuser
    `accept_ideas_simulator(n)` -
    accept the most n fair ideas

## Add new project
1. Click on your organization.
2. Click on "New project" button.
3. Provide a title and description for your project.
4. Choose the desdired access for your project: public/semi-public/ privtae.
5. Click on "Create Draft".
6. Now you can edit more basic deatils of your project.
7. Click on "Information" section and description of your project.
8. Click on "Save" (bottom of thr page).
### Add modules to your project
1. Click on "Add Module" in the project edit page.
2. Choose the module type and click on "ADD MODULE".
3. Edit and provide the module name and its description.
4. Click on "Phases" section.
5. Edit and provide the phase name and its description.
6. For "Fairvote" module type, there's only one phase:
        you must provide Start date and End date of this phase (date & time).
        participants can both add ideas and vote for them in this phase.
7. Click on "Save".
8. Click on "Add to project" switch in the module section.
9. For preview - click on "Preview" in the right side of the page.
10. For publishing - click on "Publish" in the right side of the page.
11. After publishing, you can see the project by click on "View".


## Slug Changing

### Organization Slug
This can be done via the Django shell.

1. **Activate your virtual environment** (if you are using one):
   ```bash
   source venv/bin/activate
   ```

2. **Navigate to your Django project directory**:
   ```bash
   cd /path/to/adhocracy-plus
   ```

3. **Open the Django shell**:
   ```bash
   python manage.py shell
   ```

4. **Update the organization slug by its name**:
   ```python
   # You can use another field to change by.

   # Import the necessary model
   from apps.organisations.models import Organisation

   # Retrieve the object you want to update
   obj = Organisation.objects.get(name='<org name>')  # Change the filter criteria as needed

   # Update the fields of the object
   obj.slug = '<new slug>'

   # Save the changes to the database
   obj.save()
   ```

### Project Slug
This can be done via the Django admin panel.

1. **Run the app and log in as the superuser.**
2. **Open the Django admin panel.**
3. **Select the desired project you want to change.**
4. **Update the slug field.**

