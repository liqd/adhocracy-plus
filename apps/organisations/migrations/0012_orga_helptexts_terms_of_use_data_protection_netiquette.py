# Generated by Django 2.2.11 on 2020-04-07 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("a4_candy_organisations", "0011_org_add_terms_use_data_protection_netiquette"),
    ]

    operations = [
        migrations.AlterField(
            model_name="organisation",
            name="data_protection",
            field=models.TextField(
                blank=True,
                help_text="Please provide all the legally required information of your data protection. The data protection policy will be shown on a separate page.",
                verbose_name="Data protection policy",
            ),
        ),
        migrations.AlterField(
            model_name="organisation",
            name="netiquette",
            field=models.TextField(
                blank=True,
                help_text="Please provide a netiquette for the participants. The netiquette helps improving the climate of online discussions and supports the moderation.",
                verbose_name="Netiquette",
            ),
        ),
        migrations.AlterField(
            model_name="organisation",
            name="terms_of_use",
            field=models.TextField(
                blank=True,
                help_text="Please provide all the legally required information of your terms of use. The terms of use will be shown on a separate page.",
                verbose_name="Terms of use",
            ),
        ),
    ]
