## Migration Guide: Converting Legacy `map_fields.PointField` to Django GIS `PointField`

This documentation explains how to migrate from the custom and legacy point field (`map_fields.PointField`) to Django’s standard GeoDjango `PointField`, based on the latest changes in the branch and the example from [PR #6023](https://github.com/liqd/a4-meinberlin/pull/6023/files).

So far we have migrated the projects app, for which migration field and data is happening in the adhocracy4. See relevant migrations [0048](https://github.com/liqd/adhocracy4/blob/main/adhocracy4/projects/migrations/0048_project_geos_point_project_house_number_and_more.py) and [0049](https://github.com/liqd/adhocracy4/blob/main/adhocracy4/projects/migrations/0049_migrate_data_from_point_to_geos_point.py).  

Adhocracy+ apps that need to migrate in the future:
- mapideas
- budgeting

---

### 1. Development how-to

In the following example, we outline the steps required for changing the mapideas module.

Previously, the project used a custom `PointField` from `adhocracy4.maps.fields`:

```python
# Before (legacy field)
from adhocracy4.maps import fields as map_fields

class AbstractMapIdea(models.Model):
    point = map_fields.PointField()
```

This field will be now **removed** in favor of Django’s built-in GIS field:

```python
from django.contrib.gis.db import models as gis_models

class AbstractMapIdea(models.Model):
    coordinates = gis_models.PointField(null=True, blank=True)
```

---

### 2. Migration Steps

#### Step 1: Add the New `PointField`

- Add the new GeoDjango `PointField` (`coordinates`) to your model.
- Set `null=True` and `blank=True` to allow a uninterrupted migration and make the field optional.

```python
from django.contrib.gis.db import models as gis_models

class AbstractMapIdea(models.Model):
    coordinates = gis_models.PointField(null=True, blank=True)
    street_name = models.CharField(null=True, blank=True, max_length=200)
    house_number = models.CharField(null=True, blank=True, max_length=10)
    zip_code = models.CharField(null=True, blank=True, max_length=20)
```

- Keep the old `point = map_fields.PointField()` field temporarily during migration.

#### Step 2: Create and Apply Schema Migration

- Run migrations to add the new field `coordnites`:

```bash
python manage.py makemigrations
python manage.py migrate
```

#### Step 3: Data Migration to Populate New Field

- Create a **data migration** to copy data from the old `point` field to the new `coordinates` field.

Example migration snippet:

```python
import json
import logging

from django.contrib.gis.geos import GEOSGeometry
from django.db import migrations
from django.contrib.gis.geos import Point

logger = logging.getLogger(__name__)


def migrate_point_to_coordinates(apps, schema_editor):
    MapIdea = apps.get_model('a4_candy_mapideas', 'MapIdea')
    for idea in MapIdea.objects.exclude(point__isnull=True):
        try:
	    # Handle case where point is already parsed (dict) or still a string
	    point_data = idea.point
	    if isinstance(point_data, str):
                point_data = json.loads(point_data)
                point_data = dict(point_data)

	    # Extract geometry and properties
	    geometry = point_data.get("geometry", {})
	    properties = point_data.get("properties", {})
	    if not geometry:
		logger.warning(
		    "error migrating point of idea " + idea.name + ": " + str(point_data)
		)
		continue

	    # Create GEOSGeometry from coordinates
	    if geometry.get("type") == "Point" and "coordinates" in geometry:
		geojson = {"type": "Point", "coordinates": geometry["coordinates"]}
		point = GEOSGeometry(json.dumps(geojson), srid=4326)
		# Update all fields
		MapIdea.objects.filter(id=idea.id).update(
		    coordinates=point,
		    street_name=properties.get("strname", ""),
		    house_number=properties.get("hsnr", ""),
		    zip_code=properties.get("plz", ""),
		)

	except (ValueError, TypeError, KeyError, json.JSONDecodeError) as e:
	    logger.warning(f"Skipping {project.id} {project.name}: {str(e)}")


class Migration(migrations.Migration):
    dependencies = [
        ('a4_candy_mapideas', 'previous_migration'),
    ]

    operations = [
        migrations.RunPython(migrate_point_to_coordinates),
    ]
```

- Run the migration:

```bash
python manage.py migrate
```

#### Step 4: Remove the Old `map_fields.PointField`

- After verifying the new field is populated and working correctly, remove the old `point` field from the model.

- Create and apply a migration to drop the old field with `python manage.py makemigrations` and `python manage.py migrate`

#### Step 5: Add new PointField

- If all data is migrated, add a new Geo GIS field named point and copy data from coordinates. We need to do this because a simple renaming a GeoDjango PointField (or any GIS field) directly via migrations often fails due to spatial database complexities and Django's migration detection limitations. E.g: GIS fields like PointField require special database metadata (e.g., PostGIS geometry_columns table). A simple column rename won’t update these registries, leading to broken spatial queries.


```python
# Before
coordinates = gis_models.PointField(null=True, blank=True)

# After (add a new `point` field)
coordinates = gis_models.PointField(null=True, blank=True)
point = gis_models.PointField(null=True, blank=True)
```

- Create and apply the migration to add the field running the python and migration commands as above.

#### Step 6: Copy data from `coordinates` to New PointField with a custom Migration:

```python
from django.db import migrations


def migrate_geos_point_field(apps, schema_editor):
    MapIdea = apps.get_model("a4_candy_mapideas", "MapIdea")
    for idea in MapIdea.objects.exclude(coordinates__isnull=True)():
        idea.point = idea.coordinates
        idea.save()


class Migration(migrations.Migration):

    dependencies = [
        ("a4_candy_mapideas", "previous_numbered_migration"),
    ]

    operations = [
        migrations.RunPython(
            migrate_geos_point_field, reverse_code=migrations.RunPython.noop
        ),
    ]
```

- Run the migration:

```bash
python manage.py migrate
```

#### Step 7: Remove the coordinates PointField

- After verifying the new field `point` is populated and working correctly, remove the `coordinates` field from the model.

- Create and apply a migration to drop the coordinates field.

The final version of the model will look like this:
```python

class AbstractMapIdea(models.Model):
    point = gis_models.PointField(null=True, blank=True)
    street_name = models.CharField(null=True, blank=True, max_length=200)
    house_number = models.CharField(null=True, blank=True, max_length=10)
    zip_code = models.CharField(null=True, blank=True, max_length=20)

---

### 3. Important Notes

- **Coordinate Order**: GeoDjango expects `Point(longitude, latitude)`.
- **Default Values**: When setting defaults for `PointField`, use a `Point` instance, *not* a tuple or list.
- **Database Setup**: Ensure PostGIS extension is enabled in your postgres database or use spatialite3 if working with sqlite.
- **Indexing**: Consider adding a spatial index on the new field for efficient spatial queries.

---

### 4. Summary Table

| Step  | Action                                   | Notes                                 |
|-------|------------------------------------------|---------------------------------------|
| 1     | Add new `coordinates` PointField         | Keep old `point` field temporarily    |
| 2     | Apply schema migration                   | Adds new GIS field to DB              |
| 3     | Data migration to copy data              | Run the django command migrate        |
| 4     | Remove old `point` field                 | After data verification               |
| 5     | Add new PointField `point`	           | Run makemigrations and migrate        |
| 6     | Copy data from `coordinates` to `point`  | With a custom migration               |	`
| 7     | Remove `coordinates` field               | CRun makemigrations and migrate       |	`

---

### 5. References

- [Django GeoDjango PointField docs](https://docs.djangoproject.com/en/stable/ref/contrib/gis/model-api/#pointfield)
- [How to write data migrations](https://docs.djangoproject.com/en/stable/topics/migrations/#data-migrations)
- [PostGIS setup and spatial indexing](https://postgis.net/docs/manual-3.1/postgis_installation.html)

---
