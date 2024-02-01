# Welcome to MkDocs

For full documentation visit [mkdocs.org](https://www.mkdocs.org).

## Commands

* `mkdocs new [dir-name]` - Create a new project.
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs -h` - Print help message and exit.

## Project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.

theme:
  name: "material"

nav:
  - API Reference: api.md
  - Software Architecure Reference: software_architecture.md
  - Django Shell Reference: django_shell_basics.md.md
  - Management Commands Reference: management_commands.md
  - CK Editor Reference: ckeditor.md
  - Language and Translation Reference: languages_and_translations.md
  - Production Server Installation Reference: installation_prod.md
  - Contribution Reference: contributing.md
  - Project Insights Reference: project_insights.md
  - Code Reference: reference.md
  - Celery Reference: celery.md


