# Translations

We take care to make all strings in the code (like texts on buttons, headlines that don't come from django models, ...) translatable.

The translations for the main branch are done in transifex. If you want to translate A+ into your language, please get in touch: info [at] liqd [dot] net

## Transifex
### No translations have been added locally:
#### Push new source strings to transifex
Make branch and create message files with the new strings added during development

`make po`

Test that new messages compile without any errors

`make mo`

Push updated source file with new strings to transifex to be be translated (Note: commented out strings will not be ignored by transifex, but handled as normal source strings, so remove them before from source files)

(If you do this the first time, you might need to [generate an API token](https://docs.transifex.com/account/authentication) and add it in the terminal. It will be automatically stored in your `~/.transifexrc`)

`tx push -s`

Commit and push message files to github

#### Pull new translations from transifex
Once translations have been added on transifex, create branch and force pull all translations from transifex (force is needed because the time stamps cause errors)

`tx pull -af`

Since translations files pulled from transifex have slightly different format, run

`make po`

to standardise.
Test that new messages compile without any errors

`make mo`

Then commit and push translations to github

### Translations have been added locally (DE)
Sometimes it is necessary to add DE translations directly in the .po files and
not through transifex. This method ensures no translations from DE or other
languages are overwritten and the DE translation are also added to transifex.
Create branch and ensure that all new strings are in source file

`make po`

Test that new messages and locally added translations compile without any errors

`make mo`

Push updated source file with new strings to transifex to be be translated (again, remember to first remove commented out strings from source files)

`tx push -s`

Force push locally added DE translations

`tx push -t -f -l de`

After transifex has all the translations you can then force pull and get any new
translations without risk of over-writing local german ones.

`tx pull -af`


## Extra translations in a branch or fork
When A+ is used as the basis for another project, it is important to keep
the translations from the main branch separated to be able to overwrite or
add new translations to the fork, but also keep up with new strings and
translations from the main branch.

### Enable fork-specific translations
The message files for the main branch are created by
`make po`
When the settings in base.py are untouched, this will create new message
files in the locale-source folder, where they can be translated and/or
pushed to transifex like explained above.
`make po` will also translate the English strings by themselves, meaning
that in the en folder, all missing msgstr are filled with the text from
the corresponding msgid.

When a new project is created by forking or branching, only the
translations in the locale-fork folder should be changed, so that old
translations can be kept and the fork is profiting from new translations
or translation fixes when it is rebased onto the main branch.
To create the new translations, go to the
[base settings](https://github.com/liqd/adhocracy-plus/blob/master/adhocracy-plus/config/settings/base.py)
and uncomment the first path
(os.path.join(BASE_DIR, 'locale-fork/locale')) in LOCALE_PATHS.
Now, `make po` creates message files in the locale-fork folder and
uses the translations from this folder first, whenever the messages are
compiled.
Here, the English translations are kept untranslated, so that they could
be used to overwrite strings.

### Mark fork-specific translations for translators
There are two options to mark the strings for translators:
1. By comments, that are displayed to translators. Django docs on comments for translaters
    - [in python code](https://docs.djangoproject.com/en/3.2/topics/i18n/translation/#comments-for-translators)
    - and [in templates](https://docs.djangoproject.com/en/3.2/topics/i18n/translation/#translator-comments-in-templates)
2. By using the context of the translations. Django docs on contextualizing translations
    - [in python code]](https://docs.djangoproject.com/en/3.2/topics/i18n/translation/#contextual-markers)
    - [in templates](https://docs.djangoproject.com/en/3.2/topics/i18n/translation/#std:templatetag-translate)
    - and [in js](https://docs.djangoproject.com/en/3.2/topics/i18n/translation/#pgettext)

We recommend option 1 because that is more easily changed back if the strings to translate happen to end up in the upstream repo. As of now, there is no option to add these translator comments in JavaScript code, so these have to be marked with the context option if needed.

## Adding additional languages ##
### To Wagtail CMS pages ###
Add the language to the CMS page models that you require them for. If
translations are only needed for legal pages such as Data Protection ect. then
only add language to SimplePage model as this is the page type used for all legal
information.
In translations.py add new language to either the TranslatedField (to enable
translations for all CMS page types) or TranslatedFieldLegal to just include it
for SimplePages.
When adding to all page types add fallback descriptions to settings/models.py.
### To rest of site ###
Add additional language to base.py.
Update tests.
