## Additions 

### Add new project
1. Click on your organization.
2. Click on "New project" button.
3. Provide a title and description for your project.
4. Choose the desdired access for your project: public/semi-public/ privtae.
5. Click on "Create Draft".
6. Now you can edit more basic deatils of your project.
7. Click on "Information" section and description of your project.
8. Click on "Save" (bottom of the page).

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


## Changes

### Organization Slug Changing
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

### Project Slug Changing
This can be done via the Django admin panel.

1. **Run the app and log in as the superuser.**
2. **Open the Django admin panel.**
3. **Select the desired project you want to change.**
4. **Update the slug field.**


### Text Modifications

1. **Editing Descriptions**: You can change descriptions for projects, modules, or phases through the project editing interface.

2. **Template Text Integration**: Most of the text displayed in the app is integrated into templates (html files, usually located in `templates` folders. [example](../adhocracy-plus/templates/a4modules/module_detail.html)). To make this text translatable, it should be enclosed within a translation block. Common examples include:

    ```django
    {% trans 'this is a text' %}
    ```

    ```django
    {% blocktrans %}
        Hello!
        Please register or log in.
    {% endblocktrans %}
    ```

    ```django
    {% blocktrans with name=user.name %}
        Hello {{ name }}!
        Visit your profile.
    {% endblocktrans %}
    ```

    If you are using translations in the template for the first time, remember to load the `i18n` tag.

3. **JSX Files (React)**: Some text is located in JSX files, which are used as Django `templatetags` and loaded in HTML templates. We apply translations here as well. The implementation might look like this:

   ```jsx
   import django from 'django';

   const translations = {
   upvote: django.gettext('vote'),
   };

   ...

   render() {
   return (
      ...
      <button aria-label={translations.upvote} />
   );
   }

   ...
   ```

   This ensures that texts within JSX components can also be translated similarly to the Django templates.

After adding the texts, you should run `make po`, add the tranlsations to the relevant `.po` files ([Hebrew folder](../locale-source/locale/he/LC_MESSAGES/)).
for see the translations in the app you should run `make fo`.


### Changing Ideas Per Page

To adjust the number of ideas displayed per page, follow these steps:

1. **Update `paginate_by` Field**:  
   Modify the `paginate_by` field in the `AbstractIdeaListView` class located in [views.py](../apps/ideas/views.py#65). The default value is set to 15.

2. **Adjust Fairvote Modules**:  
   For Fairvote modules, the fair acceptance order is calculated only for the first page of ideas. This value is controlled by the `MAX_ACCEPTED_IDEAS` field in [models.py](../apps/fairvote/models.py#9). If you change the number of ideas per page, make sure to adjust this field accordingly.


### Restart the server

To restart the server after making changes, run the following (you can do this as `root@csariel.xyz`):
    ```
    sudo service adhocracy-plus restart
    ```

If it doesn't work, see [installation_ariel-res.md#51] for other things to run.


## Notes

### Module and Phase Description
We define in `module_deatil.html` and `project_detail.html` templates that module and phase description one phase module,will be shown only if the text is not '.' (a dot).



## Possible Errors

### Commit Issues

#### Makefile Error

If you're unable to commit your changes and encounter a Makefile error with no detailed explanation, try the following steps:

```bash
python manage.py makemigrations
python manage.py migrate
```
