# Changelog

All notable changes to this project will be documented in this file.

Since version v2306 the format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
This project (not yet) adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v2501.4

### Added

- admin users can edit slug in the organisation admin

## v2501.3

### Changed

- change captcha helptext on contact form to be identical to the sign up form captcha
- remove the broken <br> tag from the captcha helptext and replace it with <strong>
- update translations
- update dependency stylelint-declaration-strict-value to v1.10.7
- update a4 to aplus-v2501.1.2
- update dependency glob to v11.0.1
- update dependency @babel/eslint-parser to v7.26.5
- update dependency stylelint to v16.13.0
- update dependency ignore to v7.0.3
- update dependency stylelint to v16.13.1
- update dependency sass to v1.83.4
- update dependency postcss to v8.5.0
- update dependency django to v4.2.18
- update dependency postcss to v8.5.1
- update dependency stylelint to v16.13.2



## v2501.2
### Changed
- update translations

## v2501.1
### Changed

- change sorting of past projects on organisation detail page from oldest ->
  newest to newest -> oldest (end date).
- debate delete view, replace depricated a4 DashboardComponentDeleteSignalMixin with DashboardComponentFormSignalMixin
- offlineevent delete view, replace depricated a4 DashboardComponentDeleteSignalMixin with DashboardComponentFormSignalMixin
- topicrio delete view, replace depricated a4 DashboardComponentDeleteSignalMixin with DashboardComponentFormSignalMixin
- image upload for ideas, proposals,mapideas and projects organised by date
- small css overwrites to adapt to a4 changes-  Update README with some notes and new commands for the installation of the a+ repository locally. - queryset filter for AppProjectsViewSet to include all current and future projects, and only those with enabled geolocation
- replaced the old datepicker with flatpickr
- make flatpickr instances aware of each other (e.g. for start and end phase of
  a module, you can't choose an end date which is earlier than the start date)- add a check for the creator field in the Answer/Vote signal for the poll to
accommodate the new feature to vote without registration
- update wagtail to 6.0.x
- update wagtail to 6.1.x
- update wagtail to 6.2.x
- update wagtail to 6.3 LTS
  - replace ImageChooserBlock with ImageBlock for pages and blocks
- replace chevron icon with thumbs for ratings to be consistent with changes in
  a4

### Added

- tests for image uploads and deletions for projects, organisations, interactiveevents, accounts, budgeting
- image deletion and saving docs to mkdocs index
- documentation for image saving and deletions in docs/
- AppProjectSerializer now includes the project url (#2771)
- create project dashboard component for editing location
- enable geolocation for projects from the admin in organisations
- display location item in dashboard only if enable in the organisation
- test for geolocation field and serialiser in projects
- django rest framework simplejwt for API authentication with jwt token
- translations
- add a new field `unregistered_participants` to `ProjectInsights` to allow
tracking unregistered participants in polls.
- add a signal handler for the new `poll_voted` signal which increases the
unregistered participants count in the project insights.
- docs for new open poll
- added a new make command `docs` to run the mkdocs server to read (and see live
changes to) the documentation
- info-box on poll for unregistered users
- module_description snippet with fixed semantics
### Fixed

- fix moderator feedback on comments not breaking long words/urls (#2709)
- fix moderator feedback on ideas/proposals not breaking long words/urls (#2709)
- added missing css for font sizes in ckeditor (#2765)
- added missing italic tag to bleach config (#2766)
- fix other answers in the poll-slider overlapping on long text.

### Removed

- removed the deprecated django-ckeditor fields from older migrations
- removed no longer required `use_json_field` from wagtail pages

## v2406.4
### Changed

- update a4 to aplus-v2406.4
- added djangos cookie settings to the language cookie in our custom middleware

### Fixed

- fix mixed language when changing the language via the indicator as a logged in
  user
- add missing blocktrans to account deletion email so it can be translated.
- add missing template for password_set view

## v2406.3
### Changed

- update a4 to aplus-v2406.3
- use magic as fallback to detect image filetype if MIMEImage fails to detect
  it.

## v2406.2

### Added
- modules diagrams
- added pytest-mock to dev dependencies (currently only used in forks)

### Fixed
- fixed outdated telephone number in error templates
- fixed linting errors and reformat the modified templates
- disable password help text provided by django-allauth on login form

### Changed

- changed link on error templates from hardcoded value to page root
- docs structure
- make insight migration a bit faster

## v2406.1

### Added

- add markdown rules to editorconfig
- add a changelog folder and readme with guideline for new changelog system
- add pyenv file and vim backup extension in gitignore
- custom middleware for user language
- add script to check in CI that a4 hashes for pip and npm match
- pass initial_slide as url param when going back from module to project
- in contrib templates for item_detail:
    request http referer for go back/overview to filtered/paginated list
- in topicprio templates for topic_detail:
    request http referer for go back/overview to filtered/paginated list
- in budgeting, idea, mapidea, topicprio:
    index id to be used with href anchor to navigate back to item list
- in contrib templates for map_filter_and_sort and pagination:
    index id to be used with href anchor to navigate back to item list
- logo icon and styling for project-holi btn (!7430)
- project insight model, create insight function,
  update insights with signals (#2492)
- adds support for celery task queues with a redis message broker
- adds makefile commands for starting and status checking of celery worker processes
- custom migration to make iframes work with ckeditor5
- added dependency beautifulsoup4
- add helptext to paragraph form in documents/text review
- add helptext for maptopicprio ckeditor5 field
- add helptext for topicprio ckeditor5 field
- add helptext for offlinevent ckeditor5 field
- template for github pull requests
- test helper for testing emails
- initial doc on testing
- add font-display: swap to fonts
- mkdocs generated from files inside the docs directory and docstrings in the code
- add an equal sign to the math equation in the captcha
- add new ImportantPage "registration" to wagtail
- show "Why register?" link on signup page if the new registration ImportangPage
  is set
- add option to delete account to user settings
- add new button style btn--danger-light which has a lighter red than
  btn--danger
- add new django setting APLUS_MANUAL_URL which contains a link to a manual. The
  link will get the language code + ":start" appended to account for the user
  language. If something else then dokuwiki as a target is used this needs to be
  changed in the template.
- add Help menu item to user indicator which opens the url set with
  APLUS_MANUAL_URL in a new tab
- customise django filter widget option_string by adding an html anchor
- add react-leaflet and @react-leaflet/core as dependencies (required by the new
  maps in a4)
- add djlint to lint django templates
- add alt text form field to projects and add to alt text to templates with template tag
- add alt text to project serializer to show it in moderation dashboard
- social account autoconnect to enable social account email connecting to existing regular account
- dummy provider in dev settings for testing purposes
- templates for email verification, password reset, socialaccount login, authentication error, and dummy authentication to address the template changes of allauth v.0.58.0

### Removed

- kyrgyz translation for ckeditor
- background_task_completedtask and background_task tables
- background_task app from the settings
- background_task app from the requirements
- removed frontend coverage ci actions
- removed the info text above the register button on the sign-up page
- unique email constraint
- deprecated settings for account rate limits (removed in allauth v.0.61.0)

### Fixed

- language setting as a cookie instead of session key according to django deprecation
- captcha becomes optional depending on project settings (#2449)
assets/blocks: small home page block improvements fixes #2493
assets/variables//button: rm twitter related styling and variable partial fix for #2363
apps/captcha: rm inline css and add to own file update structure to be more a11y friendly
apps/userdashboard/: small styling fixes fixes #2392
assets/variables: reduce lightening slightly on tertiary background colour fixes #2369
templates/project_list_tile: ensure abbr date title is translatable and update styling and make it hoverable on a tile link fixes #2222
assets/account: update styling for user agreements fixes #1922
- language not changing to user preference after login
- fix broken pytest-lastfailed command in Makefile
- fixed the flaky test_notify_creator_exclude_moderator test
- fixed incorrect font-style: bold
- fixed non-matching padding between background cta block and others
- fixed broken mobile styling for usecase black
- fix padding on dashboard nav dropdown for mobile
- fix dropdown caret icon not being cented on dashboard nav dropdown for mobile
- apps/userdashboard: fix wrong position of ModerationNotification dropdown on
  small screens
- add missing roles to project header tab dropdown on mobile, each tab now shows
  the correct content.
- fix badge text overflowing/not breaking on long words or sentences
- Fixed issue on `base_userdashboard.html` where the lack of word wrapping caused text to overlap.- email not rendering in unknown_account.email

### Changed

- update a4 to aplus-v2406.1
- update js dependencies
- update python dependencies
- changed wording of emails of event notifications
- replace django-ckeditor with django-ckeditor5
- disable browser-side form checks for forms which use ckeditor by adding
  `novalidate` to them  This is necessary as ckeditor form fields which are
  required will block form submission otherwise.
- update and move helptext for plans ckeditor5 field from model to form
- update and move helptext for newsletter ckeditor5 field from model to form
- update and move helptext for plattform email ckeditor5 field from model to
  form
- add image validator which validates that all img tags have the alt attribute
  set to all ckedito5 fields
- disable browser-side form checks for forms which use ckeditor by adding
  `novalidate` to them  This is necessary as ckeditor form fields which are
  required will block form submission otherwise.
- changed font-weight: normal to 400 to consistenly use numbers
- changed the register button from btn--primary to btn--secondary-filled
- changed helptext of captcha field to include an explanation on how to solve
  the captcha
- adjusted to the changed comments in a4
- the comment form now has a headline "Join the discussion"
- the comment section now has a headline "Discussion" to make the page structure
  more clear.
- add anchor to all timeline buttons / links to make the browser always show the
  main content
- Changed the default display of the chapter-detail table of contents to be open.- update jquery to 3.7.1
- update react-markdown to 9.0.1
- revert bootstrap to previous version, add rule to lock version 5.2.3 for renovate
- Django from 3.2.20 to 4.0
  - remove app label from `__init__.py` inside app directories
  - replace `re_path` with `path` for included urls.
  - remove `USE_L10N` in settings as it is now True by default
  - replace `postgresql_psycopg2` with `postgresql` in DATABASE settings
  - set admin fields description as decorators in ProjectAdminForm
  - replace deprecated `ifequal` with `if .. == ..` expression
  - replace deprecated custom `delete()` method with `form_valid()` in relevant `apps/<app-name>/views.py`
  - replace deprecated session LANGUAGE_SESSION_KEY with LANGUAGE_COOKIE_NAME cookie
  - generate migrations for related name labels
- Django from 4.0 to 4.2
  custom model save() methods should the update_fields keyword argument before calling super()
  psycopg to 3.1.18
  allauth to 0.55
- wagtail from 4.1.9 to 4.2
  - replace BaseSettings with BaseSiteSettings
  - import Site from wagtail.models instead of wagtail.core.models
  - migration for WagtailImageField which extends Django’s ImageField to use Willow for image file handling
- wagtail from 4.2 to 5.0x
  - New field for choosing css themes
    wagtail/users/migrations/0012_userprofile_theme.py
  - Migrate FieldPanel to TitleFieldPanel for slug field sync functionality
- wagtail from 5.0 to 5.1.x
- wagtail: upgrade to 5.2.x
- django-filters: upgrade to 23.5 as required by wagtail 5.2
- apps/interactiveevent: display module description and phase info as plain text
-  inherited adapter's method from get_email_confirmation_redirect_url to get_email_verification_redirect_url
-  to latest allauth v.0.63.2
- reformat CHANGELOG.md
- fixed outdated telephone number in error templates
- changed link on error templates from hardcoded value to page root
- fix linting errors and reformat the modified templates
- docs structure

## v2306

### Fixed

- projects/helpers: simplify comment filter by @goapunk in https://github.com/liqd/adhocracy-plus/pull/2450
- improve userdashboard filter performance by @goapunk in https://github.com/liqd/adhocracy-plus/pull/2449
- **warning: contains a potentially long migration!**

### Changed

- update dependency postcss to v8.4.24 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2447
- update dependency stylelint to v15.7.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2452
- update dependency sentry-sdk to v1.25.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2424
- update dependency faker to v18.10.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2428
- update dependency django-debug-toolbar to v4.1.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2426
- update dependency pytest to v7.3.2 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2453
- update dependency webpack-cli to v5.1.4 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2454
- update dependency urllib3 to v2 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2399
- update dependency wagtail to v4.1.6 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2448
- update dependency glob to v10.2.7 by @renovate in https://github.com/liqhttps://keepachangelog.com/d/adhocracy-plus/pull/2455
- update dependency postcss-loader to v7.3.3 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2456
- update dependency sass-loader to v13.3.2 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2457
- update babel monorepo to v7.22.5 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2458
- update dependency webpack to v5.86.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2460
- update dependency css-loader to v6.8.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2463
- update dependency pytest-cov to v4.1.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2459

# v2305.2

## What's Changed

- chore(deps): update dependency webpack-merge to v5.9.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2439
- fix(deps): update dependency sass-loader to v13.3.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2441
- userdashboard: use new target_creator to improve filtering by @goapunk in https://github.com/liqd/adhocracy-plus/pull/2445
- deps: update a4
- deps: update leaflet

**Full Changelog**: https://github.com/liqd/adhocracy-plus/compare/v2305...v2305.2

This release replaces the hotfix before.

# v2305.1

## What's Changed

- hotfix to be removed after proper fix: delete actions from userdashboard by @fuzzylogic2000 in https://github.com/liqd/adhocracy-plus/pull/2444

**Full Changelog**: https://github.com/liqd/adhocracy-plus/compare/v2305...v2305.1

## To do next release:

- remove one commit from release and tag on main with real fix

# v2305

## What's Changed

- chore(deps): update jest monorepo to v29.4.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2255
- chore(deps): update dependency eslint to v8.33.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2257
- chore(deps): update dependency eslint-plugin-react to v7.32.2 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2258
- fix(deps): update dependency sass to v1.58.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2263
- chore(deps): update dependency lint-staged to v13.1.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2270
- chore(deps): update jest monorepo to v29.4.2 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2273
- apps/\*/dashboard: using blueprint types for export component by @khamui in https://github.com/liqd/adhocracy-plus/pull/2272
- apps/embed: remove embed code by @fuzzylogic2000 in https://github.com/liqd/adhocracy-plus/pull/2209
- chore(deps): update dependency django to v3.2.18 [security] by @renovate in https://github.com/liqd/adhocracy-plus/pull/2278
- chore(deps): update dependency lint-staged to v13.1.2 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2279
- Jd 2023 03 account serializer lang by @goapunk in https://github.com/liqd/adhocracy-plus/pull/2282
- assets/shame: make sure comment buttons are styled by @fuzzylogic2000 in https://github.com/liqd/adhocracy-plus/pull/2283
- fix(deps): update dependency react-markdown to v8.0.5 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2243
- chore(deps): update dependency stylelint-declaration-strict-value to v1.9.2 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2285
- fix(deps): update dependency sass to v1.58.3 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2286
- chore(deps): update babel monorepo by @renovate in https://github.com/liqd/adhocracy-plus/pull/2287
- fix(deps): update dependency mini-css-extract-plugin to v2.7.3 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2289
- chore(deps): update dependency eslint to v8.35.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2288
- chore(deps): update jest monorepo to v29.5.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2291
- [#6951]scss/modal: styling modal to match design (depending on a4) by @khamui in https://github.com/liqd/adhocracy-plus/pull/2250
- chore(deps): update dependency wagtail to v4.1.2 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2269
- chore(deps): update dependency black to v23 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2264
- chore(deps): update dependency isort to v5.12.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2256
- chore(deps): update dependency faker to v16.9.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2244
- chore(deps): update dependency pytest to v7.2.2 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2231
- chore(deps): update dependency sentry-sdk to v1.16.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2247
- fix(deps): update dependency terser-webpack-plugin to v5.3.7 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2294
- chore(deps): update dependency webpack to v5.76.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2295
- fix(deps): update dependency autoprefixer to v10.4.14 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2299
- chore(deps): update dependency lint-staged to v13.2.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2300
- chore(deps): update dependency eslint to v8.36.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2301
- chore(deps): update dependency webpack to v5.76.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2303
- fix(deps): update dependency sass to v1.59.2 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2302
- chore(deps): update babel monorepo to v7.21.3 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2305
- fix(deps): update dependency sass to v1.59.3 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2306
- chore(deps): update dependency webpack to v5.76.2 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2307
- fix(deps): update dependency mini-css-extract-plugin to v2.7.5 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2309
- ideas/serializers: return localized created date by @Rineee in https://github.com/liqd/adhocracy-plus/pull/2311
- [7154] Kl 2023 03 comment mod feedback by @fuzzylogic2000 in https://github.com/liqd/adhocracy-plus/pull/2314
- Ks 2023 03 add userdashboard by @Rineee in https://github.com/liqd/adhocracy-plus/pull/2312
- apps/users//views//models//templates: using profile view as in Kosmo by @khamui in https://github.com/liqd/adhocracy-plus/pull/2313
- chore(deps): update dependency wagtail to v4.1.4 [security] by @renovate in https://github.com/liqd/adhocracy-plus/pull/2316
- chore(deps): update dependency django-allauth to v0.54.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2308
- chore(deps): update dependency whitenoise to v6.4.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2290
- chore(deps): update dependency faker to v18 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2325
- chore(deps): update dependency sentry-sdk to v1.18.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2321
- chore(deps): update dependency black to v23.3.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2320
- chore(deps): update dependency psycopg2 to v2.9.6 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2318
- chore(deps): update dependency psycopg2-binary to v2.9.6 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2319
- chore(deps): update dependency django-debug-toolbar to v4 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2323
- chore(deps): update babel monorepo to v7.21.4 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2317
- fix(deps): update dependency sass-loader to v13.2.2 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2326
- chore(deps): update eslint packages by @renovate in https://github.com/liqd/adhocracy-plus/pull/2322
- apps/users/templates: adding manual link (from settings) under profil… by @khamui in https://github.com/liqd/adhocracy-plus/pull/2315
- chore(deps): update dependency faker to v18.3.4 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2327
- chore(deps): update dependency sentry-sdk to v1.19.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2328
- [7210] userdashboard: add filters for moderation dashboard in api and use in… by @Rineee in https://github.com/liqd/adhocracy-plus/pull/2330
- chore(deps): update dependency webpack to v5.78.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2331
- fix(deps): update dependency postcss-loader to v7.2.4 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2332
- fix(deps): update dependency sass to v1.61.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2335
- chore(deps): update dependency lint-staged to v13.2.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2336
- chore(deps): update dependency eslint to v8.38.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2337
- [#7208] userdashboard clean and some a11y fixes by @philli-m in https://github.com/liqd/adhocracy-plus/pull/2333
- userdashboard/moderation: renaming by @khamui in https://github.com/liqd/adhocracy-plus/pull/2342
- apps/userdashboard/ModerationComments: add pagination to the api and … by @khamui in https://github.com/liqd/adhocracy-plus/pull/2345
- [#7208] React18 syntax and rm un-needed js from being loaded (a11y related) by @philli-m in https://github.com/liqd/adhocracy-plus/pull/2343
- [7210, 7213] Ks 2023 04 filter for reviewed comments by @Rineee in https://github.com/liqd/adhocracy-plus/pull/2346
- notifications: add moderation specific emails by @Rineee in https://github.com/liqd/adhocracy-plus/pull/2348
- [#7208] styling: userdashboard: fix project list tiles and tab location, clean comp li… by @philli-m in https://github.com/liqd/adhocracy-plus/pull/2344
- chore(deps): update dependency @testing-library/react to v14 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2292
- chore(deps): update dependency faker to v18.4.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2334
- chore(deps): update dependency webpack to v5.79.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2354
- app.js//webpack.common: update poll import so has own entrypoint a4 d… by @philli-m in https://github.com/liqd/adhocracy-plus/pull/2351
- chore(deps): update dependency postcss to v8.4.22 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2353
- fix(deps): update dependency sass to v1.62.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2355
- chore(deps): update dependency pytest to v7.3.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2338
- [7208] JS test (ModerationNotification) by @khamui in https://github.com/liqd/adhocracy-plus/pull/2349
- [#7208] a11y: lighthouse and SR improvements by @philli-m in https://github.com/liqd/adhocracy-plus/pull/2356
- chore(deps): update dependency webpack to v5.80.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2361
- chore(deps): update dependency postcss to v8.4.23 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2362
- chore(deps): update dependency webpack-cli to v5.0.2 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2366
- fix(deps): update dependency js-cookie to v3.0.4 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2367
- chore(deps): update dependency eslint to v8.39.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2368
- Ks 2023 04 moderation dashboard tests by @Rineee in https://github.com/liqd/adhocracy-plus/pull/2365
- fix(deps): update dependency js-cookie to v3.0.5 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2371
- [2252] single module project heading info added by @khamui in https://github.com/liqd/adhocracy-plus/pull/2375
- userdashboard: improve db queries for actions by @goapunk in https://github.com/liqd/adhocracy-plus/pull/2347
- [2364] badge size and colorising fix by @khamui in https://github.com/liqd/adhocracy-plus/pull/2376
- chore(deps): update dependency faker to v18.5.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2373
- fix(deps): update dependency sass to v1.62.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2380
- userdashboard/views: exclude paragraphs from comment actions by @Rineee in https://github.com/liqd/adhocracy-plus/pull/2383
- userdashboard/views: also exclude paragraphs from comment actions on … by @Rineee in https://github.com/liqd/adhocracy-plus/pull/2384
- update a4 hash by @khamui in https://github.com/liqd/adhocracy-plus/pull/2385
- translations: makemessages by @fuzzylogic2000 in https://github.com/liqd/adhocracy-plus/pull/2387
- chore(deps): update dependency webpack to v5.81.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2388
- chore(deps): update dependency lint-staged to v13.2.2 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2386
- chore(deps): update dependency stylelint to v15 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2275
- [2261 and 2262] project tile fixes by @khamui in https://github.com/liqd/adhocracy-plus/pull/2372
- badge.scss: making sure bs and a4 classes are not overwritten by .badge by @khamui in https://github.com/liqd/adhocracy-plus/pull/2381
- apps/userdashboard/ModerationNotificationList: fix packet size when f… by @khamui in https://github.com/liqd/adhocracy-plus/pull/2390
- chore(deps): update babel monorepo to v7.21.5 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2394
- fix(deps): update dependency postcss-loader to v7.3.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2395
- install urllib3 < 2 as requests doesn't support it yet by @goapunk in https://github.com/liqd/adhocracy-plus/pull/2397
- chore(deps): update babel monorepo to v7.21.8 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2402
- chore(deps): update dependency stylelint to v15.6.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2404
- a4-comments.scss: adding css for mark element using primary tint to h… by @khamui in https://github.com/liqd/adhocracy-plus/pull/2382
- Ks 2023 04 mod dashboard issues by @Rineee in https://github.com/liqd/adhocracy-plus/pull/2400
- apps/userdashboard/moderation: making image fill tile and use copyrig… by @khamui in https://github.com/liqd/adhocracy-plus/pull/2396
- chore(deps): update dependency sentry-sdk to v1.21.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2359
- chore(deps): update dependency faker to v18.6.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2393
- fix(deps): update dependency glob to v10 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2339
- [#issues] front end release issues by @philli-m in https://github.com/liqd/adhocracy-plus/pull/2391
- chore(deps): update dependency webpack to v5.82.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2406
- apps/users: adding "account already exists" email by @khamui in https://github.com/liqd/adhocracy-plus/pull/2398
- chore(deps): update dependency wagtail to v4.1.5 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2403
- chore(deps): update dependency django to v3.2.19 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2405
- chore(deps): update dependency faker to v18.6.2 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2407
- chore(deps): update dependency eslint to v8.40.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2411
- fix(deps): update dependency terser-webpack-plugin to v5.3.8 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2412
- chore(deps): update dependency webpack-cli to v5.1.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2413
- locale: makemessages by @Rineee in https://github.com/liqd/adhocracy-plus/pull/2408
- chore(deps): update dependency sentry-sdk to v1.22.2 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2410
- chore(deps): update dependency webpack-cli to v5.1.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2415
- fix(deps): update dependency glob to v10.2.3 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2417
- chore(deps): update dependency webpack to v5.82.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2419
- userdashboard: remove unused fetch of comment count by @goapunk in https://github.com/liqd/adhocracy-plus/pull/2416
- chore(deps): update dependency faker to v18.7.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2414
- styles/badge: increase specificity for badges by @khamui in https://github.com/liqd/adhocracy-plus/pull/2418
- apps//userdashboard//projects: fix tiles clickable and shadow (multim… by @khamui in https://github.com/liqd/adhocracy-plus/pull/2401
- local: add translatied strings by @philli-m in https://github.com/liqd/adhocracy-plus/pull/2420
- deps: add a4 tag by @philli-m in https://github.com/liqd/adhocracy-plus/pull/2421
- fix(deps): update dependency glob to v10.2.4 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2423
- chore(deps): update dependency stylelint to v15.6.2 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2429
- templates/\*: update text bold class for bs 5 and change selectors of … by @philli-m in https://github.com/liqd/adhocracy-plus/pull/2430
- chore(deps): update dependency webpack to v5.83.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2431
- fix(deps): update dependency glob to v10.2.5 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2432
- fix(deps): update dependency terser-webpack-plugin to v5.3.9 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2433
- fix(deps): update dependency css-loader to v6.7.4 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2435
- fix(deps): update dependency mini-css-extract-plugin to v2.7.6 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2436
- chore(deps): update dependency eslint to v8.41.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2437
- fix(deps): update dependency glob to v10.2.6 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2438

**Full Changelog**: https://github.com/liqd/adhocracy-plus/compare/v2301.1...v2305

# v2301.3

- update a4 to fix organisation terms of use checkbox in child comments
- minor style fix

Note:
This added 3 cherry-picked commits, so with the release before there are 4 to be reset before next release tagged on main.

# v2301.2

**Full Changelog**: https://github.com/liqd/adhocracy-plus/compare/v2301.1...v2301.2

Only one (cherry-picked) commit to update Django.

# v2301.1

## What's Changed

- Ks 2023 01 add black by @Rineee in https://github.com/liqd/adhocracy-plus/pull/2218
- chore(deps): update eslint packages by @renovate in https://github.com/liqd/adhocracy-plus/pull/2219
- chore(deps): update eslint packages by @renovate in https://github.com/liqd/adhocracy-plus/pull/2224
- add git-blame-ignore-revs file by @Rineee in https://github.com/liqd/adhocracy-plus/pull/2228
- chore(deps): update dependency sentry-sdk to v1.13.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2227
- chore(deps): update dependency faker to v16 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2216
- chore(deps): update dependency easy-thumbnails to v2.8.5 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2215
- Revert "add git-blame-ignore-revs file" by @fuzzylogic2000 in https://github.com/liqd/adhocracy-plus/pull/2229
- fix(deps): update dependency glob to v8.1.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2232
- chore(deps): update dependency eslint to v8.32.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2233
- organisations/forms: move brackets to right place to make string tran… by @Rineee in https://github.com/liqd/adhocracy-plus/pull/2230
- settings/base: change wording of a4_blueprint_types by @Rineee in https://github.com/liqd/adhocracy-plus/pull/2236
- translations: remove unused strings by @fuzzylogic2000 in https://github.com/liqd/adhocracy-plus/pull/2237
- rename moderatorfeedback by @khamui in https://github.com/liqd/adhocracy-plus/pull/2238
- chore(deps): update eslint packages by @renovate in https://github.com/liqd/adhocracy-plus/pull/2242
- chore(deps): update dependency @babel/runtime to v7.20.13 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2246
- chore(deps): update jest monorepo to v29.4.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2249
- [issue] update a4 to fix poll and small style and wording fixes by @phillimorland in https://github.com/liqd/adhocracy-plus/pull/2245
- Kl 2023 01 release prep by @fuzzylogic2000 in https://github.com/liqd/adhocracy-plus/pull/2253

**Full Changelog**: https://github.com/liqd/adhocracy-plus/compare/v2301...v2301.1

# v2301

## What's Changed

- apps/projects: add project contact info to app project serializer by @fuzzylogic2000 in https://github.com/liqd/adhocracy-plus/pull/1979
- chore(deps): update babel monorepo to v7.18.9 by @renovate in https://github.com/liqd/adhocracy-plus/pull/1983
- chore(deps): update jest monorepo to v28.1.3 by @renovate in https://github.com/liqd/adhocracy-plus/pull/1984
- chore(deps): update dependency markdownlint-cli to v0.32.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/1985
- chore(deps): update dependency stylelint-declaration-strict-value to v1.9.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/1986
- chore(deps): update eslint packages by @renovate in https://github.com/liqd/adhocracy-plus/pull/1987
- Ks 2022 07 module type tests and fixes by @Rineee in https://github.com/liqd/adhocracy-plus/pull/1990
- docs/api: add some curl commands by @fuzzylogic2000 in https://github.com/liqd/adhocracy-plus/pull/1989
- cms: form_data already is json in wagtail 3.x by @goapunk in https://github.com/liqd/adhocracy-plus/pull/1992
- projects/api: only allow authenticated users by @Rineee in https://github.com/liqd/adhocracy-plus/pull/1993
- chore(deps): update dependency eslint-plugin-jsx-a11y to v6.6.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/1997
- chore(deps): update dependency markdownlint-cli to v0.32.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/1998
- chore(deps): update dependency webpack to v5.74.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/1999
- account//config/urls: add account api and viewset by @Rineee in https://github.com/liqd/adhocracy-plus/pull/1994
- [6233] apps/users: add user API to get user info in app by @fuzzylogic2000 in https://github.com/liqd/adhocracy-plus/pull/1995
- config/urls: remove name of api/account by @Rineee in https://github.com/liqd/adhocracy-plus/pull/2001
- fix(deps): update dependency sass to v1.54.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2000
- settings/renovate: make renovate update py packages by @fuzzylogic2000 in https://github.com/liqd/adhocracy-plus/pull/2004
- fix(deps): update dependency autoprefixer to v10.4.8 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2005
- api: use slug to lookup projects in app by @goapunk in https://github.com/liqd/adhocracy-plus/pull/2012
- assets/images: add png fallback images by @phillimorland in https://github.com/liqd/adhocracy-plus/pull/2015
- ideas/api: do not copy request.data, but send image deletion info by @Rineee in https://github.com/liqd/adhocracy-plus/pull/2003
- Ks 2022 08 use png avatars in app by @Rineee in https://github.com/liqd/adhocracy-plus/pull/2016
- Ks 2022 08 user account api tests by @Rineee in https://github.com/liqd/adhocracy-plus/pull/2014
- Ks 2022 08 add images app user serializers by @Rineee in https://github.com/liqd/adhocracy-plus/pull/2018
- chore(deps): update eslint packages by @renovate in https://github.com/liqd/adhocracy-plus/pull/2006
- chore(deps): update babel monorepo to v7.18.10 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2019
- Jd 2022 08 local a4 by @goapunk in https://github.com/liqd/adhocracy-plus/pull/2017
- settings/renovate: allow Django versions = 3.2 by @fuzzylogic2000 in https://github.com/liqd/adhocracy-plus/pull/2022
- chore(deps): update dependency sentry-sdk to v1.9.3 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2008
- chore(deps): update dependency faker to v13.15.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2007
- chore(deps): update dependency django-cloudflare-push to v0.2.2 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2020
- chore(deps): update dependency eslint-plugin-jest to v26.8.2 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2024
- chore(deps): update dependency postcss to v8.4.16 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2026
- fix(deps): update dependency sass to v1.54.4 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2028
- chore(deps): update dependency django to v3.2.15 [security] by @renovate in https://github.com/liqd/adhocracy-plus/pull/2025
- chore(deps): update dependency django-ckeditor to v6.5.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2029
- chore(deps): update dependency sentry-sdk to v1.9.4 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2027
- chore(deps): update dependency flake8 to v5 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2010
- chore(deps): update dependency stylelint to v14.10.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2030
- fix(deps): update dependency terser-webpack-plugin to v5.3.4 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2034
- chore(deps): update dependency eslint to v8.22.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2036
- chore(deps): pin dependency @testing-library/jest-dom to 5.16.5 by @renovate in https://github.com/liqd/adhocracy-plus/pull/1974
- chore(deps): update dependency freezegun to v1.2.2 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2033
- chore(deps): update dependency stylelint-config-standard to v27 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2031
- chore(deps): update dependency faker to v14 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2037
- chore(deps): update dependency easy-thumbnails to v2.8.3 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2011
- chore(deps): update dependency eslint-plugin-jest to v26.8.3 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2038
- chore(deps): update dependency stylelint-config-standard-scss to v5 by @renovate in https://github.com/liqd/adhocracy-plus/pull/1988
- fix(deps): update dependency shpjs to v4.0.4 by @renovate in https://github.com/liqd/adhocracy-plus/pull/1973
- chore(deps): update dependency sentry-sdk to v1.9.5 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2039
- fix(deps): update dependency terser-webpack-plugin to v5.3.5 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2040
- deps: update a4 by @Rineee in https://github.com/liqd/adhocracy-plus/pull/2041
- chore(deps): update dependency eslint-plugin-jest to v26.8.4 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2044
- fix(deps): update dependency sass to v1.54.5 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2045
- chore(deps): update dependency eslint-plugin-jest to v26.8.5 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2046
- chore(deps): update dependency markdownlint-cli to v0.32.2 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2047
- chore(deps): update dependency stylelint to v14.11.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2048
- chore(deps): update dependency eslint-plugin-jest to v26.8.7 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2050
- chore(deps): update dependency eslint-plugin-n to v15.2.5 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2051
- chore(deps): update dependency @babel/core to v7.18.13 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2052
- chore(deps): update eslint packages by @renovate in https://github.com/liqd/adhocracy-plus/pull/2055
- chore(deps): update eslint packages by @renovate in https://github.com/liqd/adhocracy-plus/pull/2057
- chore(deps): update dependency eslint-plugin-jest to v26.9.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2059
- fix(deps): update dependency terser-webpack-plugin to v5.3.6 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2061
- fix(deps): update dependency sass to v1.54.6 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2062
- Pm 2022 11 a11y fixes by @phillimorland in https://github.com/liqd/adhocracy-plus/pull/2067
- chore(deps): update dependency django to v3.2.16 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2066
- chore(deps): update dependency wagtail to v3.0.3 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2063
- chore(deps): update dependency eslint-plugin-jest to v27 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2060
- chore(deps): update dependency bcrypt to v4 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2054
- chore(deps): update dependency faker to v14.2.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2042
- chore(deps): update dependency django-debug-toolbar to v3.7.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2043
- chore(deps): update dependency husky to v8.0.2 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2069
- chore(deps): update dependency django-ckeditor to v6.5.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2068
- chore(deps): update dependency stylelint to v14.15.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2080
- fix(deps): update dependency css-loader to v6.7.2 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2076
- fix(deps): update dependency autoprefixer to v10.4.13 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2074
- chore(deps): update dependency postcss to v8.4.19 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2070
- fix(deps): update dependency bootstrap to v5.2.3 by @renovate in https://github.com/liqd/adhocracy-plus/pull/1991
- chore(deps): update jest monorepo to v29 (major) by @renovate in https://github.com/liqd/adhocracy-plus/pull/2056
- chore(deps): update dependency @testing-library/react to v13.4.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2082
- chore(deps): update dependency sentry-sdk to v1.11.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2079
- chore(deps): update dependency pytest to v7.2.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2078
- chore(deps): update dependency psycopg2 to v2.9.5 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2071
- chore(deps): update dependency stylelint-declaration-strict-value to v1.9.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2073
- chore(deps): update babel monorepo by @renovate in https://github.com/liqd/adhocracy-plus/pull/2077
- chore(deps): update dependency psycopg2-binary to v2.9.5 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2072
- chore(deps): update dependency stylelint-config-standard-scss to v6 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2095
- chore(deps): update dependency pytest-cov to v4 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2093
- chore(deps): update dependency flake8 to v6 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2092
- chore(deps): update dependency faker to v15 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2091
- chore(deps): update dependency babel-loader to v9 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2090
- fix(deps): update dependency mini-css-extract-plugin to v2.7.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2087
- fix(deps): update dependency sass-loader to v13.2.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2089
- chore(deps): update dependency webpack to v5.75.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2097
- fix(deps): update dependency sass to v1.56.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2088
- chore(deps): update dependency lint-staged to v13.0.4 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2102
- [updates] rm planifolia dep and update styling part 1 by @phillimorland in https://github.com/liqd/adhocracy-plus/pull/2099
- chore(deps): update dependency stylelint-config-standard to v29 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2094
- chore(deps): update babel monorepo by @renovate in https://github.com/liqd/adhocracy-plus/pull/2106
- [updates] deps react18 by @phillimorland in https://github.com/liqd/adhocracy-plus/pull/2104
- chore(deps): update dependency zeep to v4.2.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2098
- [updates/issue] fixing styling issues from rm planifolia by @phillimorland in https://github.com/liqd/adhocracy-plus/pull/2107
- fix(deps): update dependency mini-css-extract-plugin to v2.7.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2109
- fix(deps): update dependency postcss-loader to v7.0.2 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2110
- chore(deps): update dependency wagtail to v4 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2100
- webpack.common: update to maplibre -test by @phillimorland in https://github.com/liqd/adhocracy-plus/pull/2111
- Revert "webpack.common: update to maplibre -test" by @phillimorland in https://github.com/liqd/adhocracy-plus/pull/2112
- chore(deps): update dependency webpack-cli to v5 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2101
- chore(deps): update dependency faker to v15.3.4 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2113
- chore(deps): update dependency stylelint to v14.16.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2119
- chore(deps): update dependency lint-staged to v13.1.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2121
- [updates] update mapbox to maplibre by @phillimorland in https://github.com/liqd/adhocracy-plus/pull/2115
- [updates/#6749] organisations/react_language_choice.jsx: fix linting error by @khamui in https://github.com/liqd/adhocracy-plus/pull/2116
- chore(deps): update eslint packages by @renovate in https://github.com/liqd/adhocracy-plus/pull/2085
- chore(deps): update dependency webpack-cli to v5.0.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2123
- fix(deps): update dependency mini-css-extract-plugin to v2.7.2 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2124
- chore(deps): update dependency django-debug-toolbar to v3.8.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2120
- [6751] templates/projects/module tile: redo staling of module tiles by @fuzzylogic2000 in https://github.com/liqd/adhocracy-plus/pull/2108
- [#6759] button clean up according to design clean by @phillimorland in https://github.com/liqd/adhocracy-plus/pull/2122
- chore(deps): update dependency pytest-factoryboy to v2.5.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2117
- [updates] small style fix to progress line and a4 update by @phillimorland in https://github.com/liqd/adhocracy-plus/pull/2129
- [#6750] a4dashboard: add communication form by @phillimorland in https://github.com/liqd/adhocracy-plus/pull/2081
- dashboard/phases/datetime_input: using same class to assure same heig… by @khamui in https://github.com/liqd/adhocracy-plus/pull/2131
- fix(deps): update dependency sass to v1.56.2 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2136
- chore(deps): update dependency postcss to v8.4.20 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2138
- chore(deps): update dependency django-filter to v22 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2009
- project/tiles: tile tiles do not exceed width by @khamui in https://github.com/liqd/adhocracy-plus/pull/2134
- [6751] component lib and translations by @fuzzylogic2000 in https://github.com/liqd/adhocracy-plus/pull/2137
- Ks 2022 12 social media image downlaod by @Rineee in https://github.com/liqd/adhocracy-plus/pull/2144
- chore(deps): update dependency djangorestframework to v3.14.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2084
- chore(deps): update dependency isort to v5.11.2 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2142
- dashboard/modules/publish & unpublish switch button: adding css logic… by @khamui in https://github.com/liqd/adhocracy-plus/pull/2140
- css/\_form.scss: removing spacing (margin-bottom) from input-base & ad… by @khamui in https://github.com/liqd/adhocracy-plus/pull/2125
- deps: update a4 hash and reliant packages react-flip-move and react-m… by @phillimorland in https://github.com/liqd/adhocracy-plus/pull/2150
- fix(deps): update dependency css-loader to v6.7.3 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2152
- Pm 2022 12 styling issues by @phillimorland in https://github.com/liqd/adhocracy-plus/pull/2153
- chore(deps): update dependency eslint-plugin-jest to v27.1.7 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2156
- components/item_detail.scss: setting item detail's z-index by @khamui in https://github.com/liqd/adhocracy-plus/pull/2164
- chore(deps): update dependency eslint to v8.30.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2157
- [#6754] add img format and logo checkbox by @phillimorland in https://github.com/liqd/adhocracy-plus/pull/2135
- fix(deps): update dependency sass to v1.57.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2158
- Ks 2022 12 issues by @Rineee in https://github.com/liqd/adhocracy-plus/pull/2162
- chore(deps): update dependency isort to v5.11.3 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2159
- [Issues] templates/\*: improve semantic html and add missing heading headings f… by @phillimorland in https://github.com/liqd/adhocracy-plus/pull/2169
- Kl 2022 12 blocktranslate by @fuzzylogic2000 in https://github.com/liqd/adhocracy-plus/pull/2170
- Ks 2022 12 communication form tests by @Rineee in https://github.com/liqd/adhocracy-plus/pull/2163
- chore(deps): update dependency isort to v5.11.4 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2174
- apps/projects/templates/project tile: make sure blueprint_type and ic… by @fuzzylogic2000 in https://github.com/liqd/adhocracy-plus/pull/2175
- [#6754] organisations/forms: update configs to correct differences between pi… by @phillimorland in https://github.com/liqd/adhocracy-plus/pull/2180
- organisation/views: update x axis by @phillimorland in https://github.com/liqd/adhocracy-plus/pull/2182
- Pm 2022 12 story insta by @phillimorland in https://github.com/liqd/adhocracy-plus/pull/2184
- chore(deps): update babel monorepo to v7.20.7 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2181
- sharepic: replace deprecated textsize by @goapunk in https://github.com/liqd/adhocracy-plus/pull/2186
- chore(deps): update dependency @babel/plugin-transform-modules-commonjs to v7.20.11 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2187
- replace trans with translate by @goapunk in https://github.com/liqd/adhocracy-plus/pull/2185
- sharepics: add test for aspect ratio calculation by @goapunk in https://github.com/liqd/adhocracy-plus/pull/2179
- chore(deps): update dependency easy-thumbnails to v2.8.4 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2165
- chore(deps): update dependency sentry-sdk to v1.12.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2155
- templates/buttons: using <button>s instead of <input>s as click eleme… by @khamui in https://github.com/liqd/adhocracy-plus/pull/2183
- deps/python: use moved autoslug repo by @fuzzylogic2000 in https://github.com/liqd/adhocracy-plus/pull/2188
- [6876] py packages by @fuzzylogic2000 in https://github.com/liqd/adhocracy-plus/pull/2189
- chore(deps): update dependency stylelint to v14.16.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2191
- [6876] js packages by @khamui in https://github.com/liqd/adhocracy-plus/pull/2194
- chore(deps): update dependency django-allauth to v0.52.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2192
- fix(deps): update dependency jquery to v3.6.3 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2145
- deps: update leaflet.Markercluster by @goapunk in https://github.com/liqd/adhocracy-plus/pull/2193
- Ks 2022 12 more issues by @Rineee in https://github.com/liqd/adhocracy-plus/pull/2195
- chore(deps): update dependency eslint to v8.31.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2196
- chore(deps): update dependency eslint-plugin-jest to v27.2.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2197
- fix(deps): update dependency @maplibre/maplibre-gl-leaflet to v0.0.19 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2198
- chore(deps): update dependency husky to v8.0.3 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2199
- [issues] styling issues by @phillimorland in https://github.com/liqd/adhocracy-plus/pull/2178
- [#6908] remove bcrypt from dependencies by @goapunk in https://github.com/liqd/adhocracy-plus/pull/2204
- chore(deps): update dependency @babel/core to v7.20.12 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2207
- chore(deps): update dependency babel-loader to v9.1.2 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2208
- add maplibregl-mapbox-request-transformer by @goapunk in https://github.com/liqd/adhocracy-plus/pull/2206
- chore(deps): update dependency whitenoise to v6.3.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2201
- [6876] remove django-capture-tag by @fuzzylogic2000 in https://github.com/liqd/adhocracy-plus/pull/2203
- modules/tiles/\_tile.scss: limit height to keep aspect ratio by @khamui in https://github.com/liqd/adhocracy-plus/pull/2205
- deps: update and tag a4 by @fuzzylogic2000 in https://github.com/liqd/adhocracy-plus/pull/2210
- translations: pull new strings and makemessages by @fuzzylogic2000 in https://github.com/liqd/adhocracy-plus/pull/2211
- chore(deps): update dependency eslint-plugin-jest to v27.2.1 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2212
- chore(deps): update dependency postcss to v8.4.21 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2213
- chore(deps): update dependency eslint-plugin-jsx-a11y to v6.7.0 by @renovate in https://github.com/liqd/adhocracy-plus/pull/2217
- translations: add new translations from transifex by @fuzzylogic2000 in https://github.com/liqd/adhocracy-plus/pull/2220

**Full Changelog**: https://github.com/liqd/adhocracy-plus/compare/v2207...v2301

# v2207.1

- fix cms: form_data already is json in wagtial 3.x

# v2207

## What's Changed

- apps/organisations: add model for user's agreement to organisation's terms of use
- apps/ideas, mapideas, proposals: add checkbox for org terms agreement to forms when user has not yet agreed
- apps/users: add all agreed organisation terms to user settings and make changeable
- apps/comments, poll: add agreement to comments and poll (in a4) and use
- apps/embed: remove embed code from project dashboard basic settings form
- apps/comments: only creator can edit comment
- templates/map_filter_and_sort//filter_and_sort: update filter and sorting
- templates/account settings/emails: split up actions for email-address
- js/idea_remarks.js: not working jquery selector replaced and simplify
- captcha: fix a11y and add contact info
- config/settings/organisation logo: add max_resolution
- assets/captcheck: update to logical tabbing order
- templates/errors: add template for csrf cookie 403
- deps: use own autoslug repo with fix for trailing dash
- modules: add blueprint types
- apps/offlineevents: make error message make sense by @fuzzylogic2000 in https://github.com/liqd/adhocracy-plus/pull/1960
- replace deprecated BASE_URL with WAGTAILADMIN_BASE_URL
- tests: frontend rendering tests for documents
- translations: add new translations from transifex
- fixes
- a11y improvements
- refactoring
- add tests
- deps: smaller updates
- deps: upgrade to wagtail 3
- deps: upgrade React

**Full Changelog**: https://github.com/liqd/adhocracy-plus/compare/v2202.1...v2207

# v2202.2

Changes are:

- update Django to 3.2.13

Note:

- one hot-fix commit on the release-branch, that needs to be removed before next release.

# v2202.1

Changes are:

- minor updates
- CK editor setting adaptions
- comment style fixes

Note: target main - no cherry-picked commits on release

# v2202

Changes include:

- move export functions to a4 and use
- added general error messages to top of user forms with validation errors
- new translations
- use own CK editor embed provider
- disallow adding image links in CK editor
- fix report email link for redirected sites
- update Django to v 3.2
- lots of updates
- lots of styling, wording, a11y, and bug fixes

# v2110.2

- fixes #1548

Note:
-> commit 3a1298893a1194b5900cc1975e71bb970c4b4400 is cherry-picked from main and has to be reset on next release
-> by now release has to be reset by two commits

# v2110.1

- fixes issue #1547

Note:
-> commit 50c50e016b25ebfcc54ad4b7fab72998df91d2fa is cherry-picked from main and has to be reset on next release

# v2110

Changes include:

- add idea API to be used with app
- add module and project APIs to be used with app
- add token authentification to be used with app
- use export code from a4
- migrate polls to a4 polls and use a4 code
- add open questions to poll
- add "other" option to vote questions for poll
- replace dashboard project progress circle with line
- add cookie remembering the collapsed dashboard project navs
- more tests
- lots of updates
- update to bootstrap 5
- lots of fixes

# v2105.1

Changes:

- add validation to make double voting on polls impossible

# v2105

Changes are:

- improve interactive event info and add image
- make affiliation in interactive event setup required
- send welcome email to participants of private and semi-public projects
- added basic idea serializer
- a11y improvements
- add more tests
- improvements to docs
- issue and style fixes
- new translations
- updates

# v2103

- captcha for registration and wagtail contact form
- added languages ru and ky
- make wagtail simple pages translatable to all page languages
- make platform name settable in wagtail
- update translations
- refactoring
- issue fixes and small improvements
- lots of updates

# v2012.2

Update A4 to fix https://github.com/liqd/adhocracy4/issues/644

# v2012.1

Fix some more issue that came up during testing, including https://github.com/liqd/adhocracy-plus/issues/1023, https://github.com/liqd/adhocracy-plus/issues/1024 and https://github.com/liqd/adhocracy-plus/issues/1028

# v2012

- update packages incl. a4
- issue fixes incl. organication page menu on mobile
- templates: always oganisation from view
- cms: ensure only existing page types can be chosen
- add error message for deleted invites
- translations, wording issue fixes incl. ihre profil
- a4-comment issue fixes - move btn to right, add padding
- linting: exclude isort in migrations, rm unused polylint
- ckeditor embed added to results and info tab ckeditor
- livestream: add embed ck editor to interactive event, include cookie overlay, add tests for livestream
- interactive-event: merge questions and like into app
- organisation: remove old untranslated fields
- newsletter\_ add helptext and max image width
- django-admin: remove topic and location
- interactive-event: add react question component, rm old question form, style, add test, add char count, page anchor at bottom of list, only show stats when categories.
- remove unverified users
- change logo back to normal

# v2011.2

- fix is_public in organisation sitemap

# v2011

Changes include:

- translatable organisation fields
- organisation language as fallback for invitation emails
- cookieless matomo-tracking
- addition of semi-public projects
- make email strings translatable (in transifex)
- bugfixes
- lots of updates
- lots of styling fixes
- cleanup
- more tests
- additions to the docs
- more translations
- happy birthday a+: changed logo

# v2006.1

Some last minute fixes, see https://github.com/liqd/adhocracy-plus/pull/666

# v2006

aintenance release.

# v2002.4

Fixed some more minor issues

# v2002.3

- minor wording changes

# v2002.2

- add extra checkbox to igbce registration
- show more info organisation admin
- small styling fixes

# v2002.1

- made async emails site aware
- fixed some small issues
