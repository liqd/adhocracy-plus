# CKEditor

We use the ckeditor in the dashboard for information and result inputs and also user side for idea adding. This allows users to add formatted text, editable images, accordions and videos. To achieve this we have 4 configured editors for different use cases, default (ideas), image-editor, collapsible-image-editor(information, results), video-editor(live stream).

## Editor
-   We use [django-ckeditor](https://pypi.org/project/django-ckeditor/) which utilises [ckeditor 4.7](https://ckeditor.com/docs/ckeditor4/latest/index.html).

## Configs
-   The configs of the editors can be found in base.py.
-   Config options can be found [here](https://ckeditor.com/docs/ckeditor4/latest/api/CKEDITOR_config.html) syntax is slightly different for django-ckeditor (see removeDialogTabs). Official [example config](https://github.com/django-ckeditor/django-ckeditor#example-ckeditor-configuration).

## Dialog windows
-   The dialog windows which open when addinga  link, image, ect. can be customised via [CKEditor Dialog API](https://ckeditor.com/docs/ckeditor4/latest/api/CKEDITOR_dialog.html).
-   An example of this can be seen in app.js where the code snippet is deleting the URL input in the image dialog, futher examples can be found [here](https://docs.cksource.com/CKEditor_3.x/Howto/Editing_Dialog_Windows) and [here](https://ckeditor.com/old/forums/Support/How-remove-Element-particular-Tab#comment-62739).
-   NOTE: The id/name of the input you wish to delete will follow the naming conventions in the examples but will not be the id from the rendered page.

## Plugins
-   To add plugins, it should be done in a4 in adhocracy4/ckeditor, then update config in aplus (see embedbase), not all ckeditor plugins can be used in django-ckeditor, see below for a list.
-   It is possible to create custom plugins (see collapsibleItem in a4).
-   The embed plugin we use also uses a self hosted version of iframely in order to serve iframes from a urls, configs are found in admin repository.

### Allowed plugins

a11yhelp, about, adobeair, ajax, autoembed, autogrow, autolink, bbcode, clipboard, codesnippet,
codesnippetgeshi, colordialog, devtools, dialog, div, divarea, docprops, embed, embedbase,
embedsemantic, filetools, find, flash, forms, iframe, iframedialog, image, image2, language,
lineutils, link, liststyle, magicline, mathjax, menubutton, notification, notificationaggregator,
pagebreak, pastefromword, placeholder, preview, scayt, sharedspace, showblocks, smiley,
sourcedialog, specialchar, stylesheetparser, table, tableresize, tabletools, templates, uicolor,
uploadimage, uploadwidget, widget, wsc, xml
