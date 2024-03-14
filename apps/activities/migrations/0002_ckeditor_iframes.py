# Generated by Django 3.2.20 on 2023-11-16 11:35

from bs4 import BeautifulSoup
from django.db import migrations


def replace_iframe_with_figur(apps, schema_editor):
    template = (
        '<figure class="media"><div data-oembed-url="{url}"><div><iframe src="'
        '{url}"></iframe></div></div></figure>'
    )
    Activity = apps.get_model("a4_candy_activities", "Activity")
    for activity in Activity.objects.all():
        soup = BeautifulSoup(activity.description, "html.parser")
        iframes = soup.findAll("iframe")
        for iframe in iframes:
            figure = BeautifulSoup(
                template.format(url=iframe.attrs["src"]), "html.parser"
            )
            iframe.replaceWith(figure)
        if iframes:
            activity.live_stream = soup.prettify(formatter="html")
            activity.save()


class Migration(migrations.Migration):
    dependencies = [
        ("a4_candy_activities", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            replace_iframe_with_figur,
        ),
    ]
