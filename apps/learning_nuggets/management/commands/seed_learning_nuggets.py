from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from wagtail.models import Page

from apps.learning_nuggets.models import LearningCategory
from apps.learning_nuggets.models import LearningCenterPage
from apps.learning_nuggets.models import LearningNuggetPage

DEMO_SLUG_PREFIX = "demo-"

CATEGORIES = [
    {
        "slug": "demo-erste-schritte",
        "name": "Erste Schritte",
        "description": "Grundlagen für neue Nutzer:innen.",
        "permission_level": "teilnehmer:in",
        "order": 10,
    },
    {
        "slug": "demo-profil",
        "name": "Profil & Konto",
        "description": "Profil, Passwort und Anmeldung.",
        "permission_level": "teilnehmer:in",
        "order": 20,
    },
    {
        "slug": "demo-beteiligung",
        "name": "Beteiligung",
        "description": "Ideen, Kommentare und Abstimmungen.",
        "permission_level": "teilnehmer:in",
        "order": 30,
    },
    {
        "slug": "demo-projekte",
        "name": "Projekte anlegen",
        "description": "Projekte erstellen und verwalten.",
        "permission_level": "initiator:in",
        "order": 40,
    },
    {
        "slug": "demo-moderation",
        "name": "Moderation",
        "description": "Inhalte prüfen und moderieren.",
        "permission_level": "moderator:in",
        "order": 50,
    },
]

NUGGETS = [
    {
        "slug": "demo-profil-einrichten",
        "title": "Profil einrichten",
        "category": "demo-erste-schritte",
        "order": 10,
        "blocks": [
            {
                "title": "Profil anlegen",
                "description": (
                    "<p>Öffne dein Profil über das Menü oben rechts und "
                    "ergänze Name, Bild und Benachrichtigungen.</p>"
                ),
            },
            {
                "title": "Profil bearbeiten",
                "description": (
                    "<p>Du kannst dein Profil jederzeit bearbeiten. "
                    "Änderungen werden sofort übernommen.</p>"
                ),
            },
        ],
    },
    {
        "slug": "demo-konto-verwalten",
        "title": "Konto verwalten",
        "category": "demo-profil",
        "order": 20,
        "blocks": [
            {
                "title": "Passwort zurücksetzen",
                "description": (
                    "<p>Wenn du dein Passwort vergessen hast, fordere über "
                    "die Anmeldeseite eine E-Mail zum Zurücksetzen an.</p>"
                ),
            },
            {
                "title": "E-Mail-Adresse ändern",
                "description": (
                    "<p>Die E-Mail-Adresse lässt sich in den "
                    "Kontoeinstellungen ändern.</p>"
                ),
            },
        ],
    },
    {
        "slug": "demo-registrierung",
        "title": "Registrierung und Anmeldung",
        "category": "demo-erste-schritte",
        "order": 30,
        "blocks": [
            {
                "title": "Willkommen bei adhocracy+",
                "description": (
                    "<p>Registriere dich mit deiner E-Mail-Adresse und "
                    "bestätige anschließend den Link in der E-Mail.</p>"
                ),
            },
        ],
    },
    {
        "slug": "demo-ideen-einreichen",
        "title": "Ideen einreichen",
        "category": "demo-beteiligung",
        "order": 40,
        "blocks": [
            {
                "title": "Eine Idee erstellen",
                "description": (
                    "<p>Beschreibe deine Idee möglichst konkret und reiche "
                    "sie anschließend zur Abstimmung ein.</p>"
                ),
            },
        ],
    },
    {
        "slug": "demo-projekt-anlegen",
        "title": "Projekt anlegen",
        "category": "demo-projekte",
        "order": 50,
        "blocks": [
            {
                "title": "Neues Projekt starten",
                "description": (
                    "<p>Lege ein Projekt an, wähle die passenden Module und "
                    "veröffentliche es anschließend.</p>"
                ),
            },
            {
                "title": "Projekt veröffentlichen",
                "description": (
                    "<p>Erst nach der Veröffentlichung ist das Projekt für "
                    "Teilnehmer:innen sichtbar.</p>"
                ),
            },
        ],
    },
    {
        "slug": "demo-kommentare-moderieren",
        "title": "Kommentare moderieren",
        "category": "demo-moderation",
        "order": 60,
        "blocks": [
            {
                "title": "Kommentar ausblenden",
                "description": (
                    "<p>Ausgeblendete Kommentare bleiben für die Moderation "
                    "sichtbar, werden aber nicht mehr öffentlich angezeigt.</p>"
                ),
            },
            {
                "title": "Meldung bearbeiten",
                "description": (
                    "<p>Prüfe gemeldete Beiträge und entscheide, ob sie "
                    "freigegeben oder entfernt werden.</p>"
                ),
            },
        ],
    },
    {
        "slug": "demo-datenschutz",
        "title": "Datenschutz & Sicherheit",
        "category": "demo-profil",
        "order": 70,
        "blocks": [
            {
                "title": "Daten & Privatsphäre",
                "description": (
                    "<p>Hier findest du Hinweise zum Umgang mit deinen "
                    "Daten und zur Sicherheit deines Kontos.</p>"
                ),
            },
        ],
    },
    {
        "slug": "demo-entwurf-passwort",
        "title": "Entwurf: Passwort-Reset",
        "category": "demo-profil",
        "order": 80,
        "draft": True,
        "blocks": [
            {
                "title": "Passwort-Reset (Entwurf)",
                "description": (
                    "<p>Dieser Nugget ist absichtlich nicht veröffentlicht "
                    "und darf in der Suche nicht auftauchen.</p>"
                ),
            },
        ],
    },
]


class Command(BaseCommand):
    help = (
        "Create demo categories and learning nuggets for trying out the "
        "sidebar search. Existing demo data is updated in place; use --reset "
        "to delete it first."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing demo pages and categories before seeding.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Only print what would be created; do not write anything.",
        )

    def handle(self, *args, **options):
        reset = options["reset"]
        dry_run = options["dry_run"]

        if reset:
            deleted_pages, deleted_categories = self._delete_demo_data(dry_run)
            if dry_run:
                self.stdout.write(
                    f"Would delete {deleted_pages} demo pages and "
                    f"{deleted_categories} demo categories."
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Deleted {deleted_pages} demo pages and "
                        f"{deleted_categories} demo categories."
                    )
                )

        center = self._get_or_create_center(dry_run)
        if dry_run:
            self.stdout.write(
                f"Would seed {len(NUGGETS)} demo nuggets in "
                f"{len(CATEGORIES)} categories under {center.title!r}."
            )
            return

        categories = self._create_categories()
        created, updated, drafts = self._create_nuggets(center, categories)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded learning nuggets under {center.title!r}: "
                f"{created} created, {updated} updated, {drafts} draft(s)."
            )
        )
        self.stdout.write(
            "Try the sidebar search with: Profil, Passwort, regist, Projekt, "
            "Moderation, Datenschutz."
        )

    def _get_or_create_center(self, dry_run):
        center = LearningCenterPage.objects.first()
        if center:
            if not center.live:
                if dry_run:
                    self.stdout.write(
                        "Would publish the existing Learning Center page."
                    )
                else:
                    center.save_revision().publish()
            return center

        root = Page.get_first_root_node()
        home = root.get_children().first() if root else None
        if home is None:
            raise CommandError(
                "No homepage found. Create a homepage in Wagtail first, then "
                "run this command again."
            )

        if dry_run:
            return LearningCenterPage(title="Learning Center")

        center = LearningCenterPage(title="Learning Center", slug="learning-center")
        home.add_child(instance=center)
        center.save_revision().publish()
        self.stdout.write(
            self.style.SUCCESS(f"Created Learning Center page at {center.url}.")
        )
        return center

    def _create_categories(self):
        categories = {}
        for data in CATEGORIES:
            category, _ = LearningCategory.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "name": data["name"],
                    "description": data["description"],
                    "permission_level": data["permission_level"],
                    "order": data["order"],
                },
            )
            categories[category.slug] = category
        return categories

    def _create_nuggets(self, center, categories):
        created = updated = drafts = 0

        for data in NUGGETS:
            category = categories[data["category"]]
            content = [("learning_nugget", block) for block in data.get("blocks", [])]
            page = (
                LearningNuggetPage.objects.child_of(center)
                .filter(slug=data["slug"])
                .first()
            )
            is_draft = data.get("draft", False)

            if page is None:
                page = LearningNuggetPage(
                    title=data["title"],
                    slug=data["slug"],
                    category=category,
                    content=content,
                    order=data["order"],
                    live=not is_draft,
                )
                center.add_child(instance=page)
                created += 1
            else:
                page.title = data["title"]
                page.category = category
                page.content = content
                page.order = data["order"]
                page.save()
                updated += 1

            if is_draft:
                if page.live:
                    page.unpublish()
                else:
                    page.save()
                drafts += 1
            else:
                page.save_revision().publish()

        return created, updated, drafts

    def _delete_demo_data(self, dry_run):
        pages = LearningNuggetPage.objects.filter(slug__startswith=DEMO_SLUG_PREFIX)
        categories = LearningCategory.objects.filter(slug__startswith=DEMO_SLUG_PREFIX)

        page_count = pages.count()
        category_count = categories.count()
        if dry_run:
            return page_count, category_count

        for page in pages:
            page.delete()
        categories.delete()
        return page_count, category_count
