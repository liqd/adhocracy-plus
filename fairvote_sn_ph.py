import os
import django

from allauth.account.models import EmailAddress
from django.contrib.contenttypes.models import ContentType

from adhocracy4.modules.models import Module
from adhocracy4.phases.models import Phase
from adhocracy4.ratings.models import Rating
from apps.fairvote.models import Choin
from apps.fairvote.models import Idea
from apps.fairvote.models import IdeaChoin
from apps.fairvote.phases import FairVotePhase
from apps.organisations.models import Organisation
from apps.projects.models import Project
from apps.users.models import User
from apps.ideas.forms import IdeaForm, IdeaModerateForm
from apps.fairvote.api import IdeaChoinViewSet
from django.http.request import HttpRequest
from adhocracy4.projects.models import Access
from adhocracy4.rules.discovery import NormalUser
from apps.organisations.models import OrganisationTermsOfUse
from apps.fairvote.algorithms import update_ideas_acceptance_order
import logging

# should be below 'os' and 'django' imports
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "adhocracy-plus.config.settings")
django.setup()

logger = logging.getLogger(__name__)


"""
1. submit idea
2. all users vote for it
3. check the idea choins, and missing
4. accept idea
5. check users balance - including not supporting users
6. optional: check other ideas choins
"""

idea_list = [
    {
        "name": "צפון - שיפוץ גני המשחקים בישוב",
        "description": "בגני המשחקים בישוב חסרות נדנדות לפעוטות, יש המון לכלוך והמתקנים ישנים ומרוססים בגרפיטי. הילדים שלנו צריכים גני משחקים נקיים ובטוחים למשחק!",
    },
    {
        "name": "צפון - הקמת פינות פיקניק",
        "description": "להקים פינות פיקניק מסודרות עם שולחנות, ספסלים וגרילים ציבוריים בפארקים המרכזיים, לטובת משפחות וקהילות שרוצות לבלות יחד בטבע.",
    },
    {
        "name": "צפון - שיפור מערכת התחבורה הציבורית",
        "description": "לשפר את קווי האוטובוס ולהוסיף תחנות חדשות, במיוחד באזורים מרוחקים של היישוב, כדי להקל על הניידות ולצמצם את השימוש ברכבים פרטיים.",
    },
    {
        "name": "צפון - מרכז קהילתי חדש",
        "description": "להקים מרכז קהילתי חדש עם פעילויות מגוונות כמו חוגי ספורט, אומנויות ובישול, שיתאימו לכל הגילאים ויחזקו את תחושת הקהילה.",
    },
    {
        "name": "צפון - פיתוח שבילי אופניים",
        "description": "לסלול שבילי אופניים בטוחים ונגישים ברחבי היישוב, כדי לעודד רכיבה בטוחה ואורח חיים בריא יותר.",
    },
    {
        "name": "צפון - הקמת גינות קהילתיות",
        "description": "להקים גינות קהילתיות שבהן התושבים יוכלו לגדל ירקות וצמחי תבלין, ולחזק את הקשר בין האנשים לטבע.",
    },
    {
        "name": "צפון - פרויקט אמנות ציבורית",
        "description": "לקדם פרויקטים של אמנות ציבורית, כמו ציורי קיר ופסלים, שיתרמו לאסתטיקה של היישוב ויתמכו באמנים מקומיים.",
    },
    {
        "name": "צפון - הגברת הביטחון האישי",
        "description": "להוסיף תאורה ברחובות חשוכים ולהתקין מצלמות אבטחה באזורים מועדים לפורענות, כדי להעלות את תחושת הביטחון של התושבים.",
    },
    {
        "name": "צפון - שיפור מערכת הביוב והניקוז",
        "description": "לבצע עבודות תחזוקה ושיפור למערכת הביוב והניקוז כדי למנוע הצפות ולשפר את איכות החיים.",
    },
    {
        "name": "צפון - הקמת מגרש ספורט רב-תכליתי",
        "description": "להקים מגרש ספורט פתוח עם מתקנים לכדורסל, כדורגל וטניס, לטובת פעילות ספורטיבית חופשית של כל הגילאים.",
    },
    {
        "name": "צפון - פיתוח מסלולי הליכה וריצה",
        "description": "לסלול מסלולי הליכה וריצה בפארקים ובשדות הפתוחים, לטובת תושבים שרוצים לעסוק בפעילות גופנית בטבע.",
    },
    {
        "name": "צפון - הקמת מרכז למידה דיגיטלי",
        "description": "להקים מרכז למידה עם מחשבים וגישה לאינטרנט, שבו ילדים ומבוגרים יוכלו ללמוד ולהתפתח בתחומים שונים.",
    },
    {
        "name": "צפון - הקמת תיאטרון קהילתי",
        "description": "להקים תיאטרון קטן שיארח הצגות ומופעים מקומיים, ויהיה מקום מפגש תרבותי לתושבים.",
    },
    {
        "name": "צפון - שיפור הנגישות לבעלי מוגבלויות",
        "description": "לשפר את התשתיות כדי לאפשר נגישות מלאה לבעלי מוגבלויות בכל אזורי היישוב, כולל מדרכות, מבנים ציבוריים ותחנות תחבורה.",
    },
    {
        "name": "צפון - הקמת מרכז יוגה ומדיטציה",
        "description": "להקים מרכז יוגה ומדיטציה שבו יתקיימו שיעורים והדרכות לתושבים המעוניינים באורח חיים רגוע ובריא יותר.",
    },
    {
        "name": "צפון - פיתוח פארק טבע עירוני",
        "description": "להקים פארק טבע עם צמחיה מקומית, בריכות ומסלולים אקולוגיים, שיאפשרו לתושבים להתחבר לטבע וללמוד עליו.",
    },
    {
        "name": "צפון - הקמת תחנת מחזור מרכזית",
        "description": "להקים תחנת מחזור מרכזית שבה התושבים יוכלו להפריד פסולת ולתרום לשמירה על איכות הסביבה.",
    },
    {
        "name": "צפון - הקמת שוק איכרים מקומי",
        "description": "להקים שוק איכרים שבו יימכרו מוצרים מקומיים טריים ואיכותיים, ויהווה מקום מפגש חברתי לכל התושבים.",
    },
    {
        "name": "צפון - הקמת ספרייה קהילתית",
        "description": "להקים ספרייה עם ספרים, מגזינים ומשאבי למידה, שתשמש מקום מפגש תרבותי וחינוכי לכל הגילאים.",
    },
    {
        "name": "צפון - פיתוח תכניות חינוך סביבתי",
        "description": "לפיתוח ולהפעיל תכניות חינוך סביבתי בבתי הספר ובקהילה, להעלאת המודעות והכישורים של התושבים בנושא שמירה על הסביבה.",
    },
    {
        "name": "דרום - שיפוץ גני המשחקים בישוב",
        "description": "בגני המשחקים בישוב חסרות נדנדות לפעוטות, יש המון לכלוך והמתקנים ישנים ומרוססים בגרפיטי. הילדים שלנו צריכים גני משחקים נקיים ובטוחים למשחק!",
    },
    {
        "name": "דרום - הקמת פינות פיקניק",
        "description": "להקים פינות פיקניק מסודרות עם שולחנות, ספסלים וגרילים ציבוריים בפארקים המרכזיים, לטובת משפחות וקהילות שרוצות לבלות יחד בטבע.",
    },
    {
        "name": "דרום - שיפור מערכת התחבורה הציבורית",
        "description": "לשפר את קווי האוטובוס ולהוסיף תחנות חדשות, במיוחד באזורים מרוחקים של היישוב, כדי להקל על הניידות ולצמצם את השימוש ברכבים פרטיים.",
    },
    {
        "name": "דרום - מרכז קהילתי חדש",
        "description": "להקים מרכז קהילתי חדש עם פעילויות מגוונות כמו חוגי ספורט, אומנויות ובישול, שיתאימו לכל הגילאים ויחזקו את תחושת הקהילה.",
    },
    {
        "name": "דרום - פיתוח שבילי אופניים",
        "description": "לסלול שבילי אופניים בטוחים ונגישים ברחבי היישוב, כדי לעודד רכיבה בטוחה ואורח חיים בריא יותר.",
    },
    {
        "name": "דרום - הקמת גינות קהילתיות",
        "description": "להקים גינות קהילתיות שבהן התושבים יוכלו לגדל ירקות וצמחי תבלין, ולחזק את הקשר בין האנשים לטבע.",
    },
    {
        "name": "דרום - פרויקט אמנות ציבורית",
        "description": "לקדם פרויקטים של אמנות ציבורית, כמו ציורי קיר ופסלים, שיתרמו לאסתטיקה של היישוב ויתמכו באמנים מקומיים.",
    },
    {
        "name": "דרום - הגברת הביטחון האישי",
        "description": "להוסיף תאורה ברחובות חשוכים ולהתקין מצלמות אבטחה באזורים מועדים לפורענות, כדי להעלות את תחושת הביטחון של התושבים.",
    },
    {
        "name": "דרום - שיפור מערכת הביוב והניקוז",
        "description": "לבצע עבודות תחזוקה ושיפור למערכת הביוב והניקוז כדי למנוע הצפות ולשפר את איכות החיים.",
    },
    {
        "name": "דרום - הקמת מגרש ספורט רב-תכליתי",
        "description": "להקים מגרש ספורט פתוח עם מתקנים לכדורסל, כדורגל וטניס, לטובת פעילות ספורטיבית חופשית של כל הגילאים.",
    },
    {
        "name": "דרום - פיתוח מסלולי הליכה וריצה",
        "description": "לסלול מסלולי הליכה וריצה בפארקים ובשדות הפתוחים, לטובת תושבים שרוצים לעסוק בפעילות גופנית בטבע.",
    },
    {
        "name": "דרום - הקמת מרכז למידה דיגיטלי",
        "description": "להקים מרכז למידה עם מחשבים וגישה לאינטרנט, שבו ילדים ומבוגרים יוכלו ללמוד ולהתפתח בתחומים שונים.",
    },
    {
        "name": "דרום - הקמת תיאטרון קהילתי",
        "description": "להקים תיאטרון קטן שיארח הצגות ומופעים מקומיים, ויהיה מקום מפגש תרבותי לתושבים.",
    },
    {
        "name": "דרום - שיפור הנגישות לבעלי מוגבלויות",
        "description": "לשפר את התשתיות כדי לאפשר נגישות מלאה לבעלי מוגבלויות בכל אזורי היישוב, כולל מדרכות, מבנים ציבוריים ותחנות תחבורה.",
    },
    {
        "name": "דרום - הקמת מרכז יוגה ומדיטציה",
        "description": "להקים מרכז יוגה ומדיטציה שבו יתקיימו שיעורים והדרכות לתושבים המעוניינים באורח חיים רגוע ובריא יותר.",
    },
    {
        "name": "דרום - פיתוח פארק טבע עירוני",
        "description": "להקים פארק טבע עם צמחיה מקומית, בריכות ומסלולים אקולוגיים, שיאפשרו לתושבים להתחבר לטבע וללמוד עליו.",
    },
    {
        "name": "דרום - הקמת תחנת מחזור מרכזית",
        "description": "להקים תחנת מחזור מרכזית שבה התושבים יוכלו להפריד פסולת ולתרום לשמירה על איכות הסביבה.",
    },
    {
        "name": "דרום - הקמת שוק איכרים מקומי",
        "description": "להקים שוק איכרים שבו יימכרו מוצרים מקומיים טריים ואיכותיים, ויהווה מקום מפגש חברתי לכל התושבים.",
    },
    {
        "name": "דרום - הקמת ספרייה קהילתית",
        "description": "להקים ספרייה עם ספרים, מגזינים ומשאבי למידה, שתשמש מקום מפגש תרבותי וחינוכי לכל הגילאים.",
    },
    {
        "name": "דרום - פיתוח תכניות חינוך סביבתי",
        "description": "לפיתוח ולהפעיל תכניות חינוך סביבתי בבתי הספר ובקהילה, להעלאת המודעות והכישורים של התושבים בנושא שמירה על הסביבה.",
    },
]


users_list = [
    {"name": "יוסי כהן צפון", "email": "nyossi.cohen@examplexyz.com"},
    {"name": "אבי לוי צפון", "email": "navi.levi@examplexyz.com"},
    {"name": "דוד שמעון צפון", "email": "ndavid.shimon@examplexyz.com"},
    {"name": "אלי בר צפון", "email": "neli.bar@examplexyz.com"},
    {"name": "איתי הלוי צפון", "email": "nitai.halevi@examplexyz.com"},
    {"name": "רון בן דוד צפון", "email": "nron.bendavid@examplexyz.com"},
    {"name": "יעל אזולאי צפון", "email": "nyael.azoulay@examplexyz.com"},
    {"name": "תמר כרמי צפון", "email": "ntamar.carmi@examplexyz.com"},
    {"name": "ליאת שלו צפון", "email": "nliat.shalev@examplexyz.com"},
    {"name": "שירה מלכה צפון", "email": "nshira.malka@examplexyz.com"},
    {"name": "גדי נוי צפון", "email": "ngadi.noy@examplexyz.com"},
    {"name": "הילה ברוך צפון", "email": "nhila.baruch@examplexyz.com"},
    {"name": "ירון פרץ צפון", "email": "nyaron.peretz@examplexyz.com"},
    {"name": "מאיה כהן צפון", "email": "nmaya.cohen@examplexyz.com"},
    {"name": "עומר בן שמעון צפון", "email": "nomer.benshimon@examplexyz.com"},
    {"name": "דנה שרעבי צפון", "email": "ndana.sharabi@examplexyz.com"},
    {"name": "נועם עמית דרום", "email": "snoam.amit@examplexyz.com"},
    {"name": "עופר גולן דרום", "email": "sofer.golan@examplexyz.com"},
    {"name": "ליאור כץ דרום", "email": "slior.katz@examplexyz.com"},
    {"name": "רוני לוי דרום", "email": "sroni.lavi@examplexyz.com"},
    {"name": "נטע שירן דרום", "email": "sneta.shiran@examplexyz.com"},
    {"name": "אורלי אביב דרום", "email": "sorly.aviv@examplexyz.com"},
    {"name": "טליה גל דרום", "email": "stalia.gal@examplexyz.com"},
    {"name": "רמי זוהר דרום", "email": "srami.zohar@examplexyz.com"},
    {"name": "עדן רז דרום", "email": "sedan.raz@examplexyz.com"},
    {"name": "אורית הראל דרום", "email": "sorit.harel@examplexyz.com"},
    {"name": "עמית בן עמי דרום", "email": "samit.benami@examplexyz.com"},
    {"name": "עידו בן יוסף דרום", "email": "sido.benyosef@examplexyz.com"},
    {"name": "גלי לוין דרום", "email": "sgali.levin@examplexyz.com"},
    {"name": "ניר ארבל דרום", "email": "snir.arbel@examplexyz.com"},
    {"name": "ליעד שגיא דרום", "email": "sliad.sagi@examplexyz.com"},
    {"name": "הדס שמר דרום", "email": "shadas.shemer@examplexyz.com"},
    {"name": "מורן גליק דרום", "email": "smoran.glick@examplexyz.com"},
    {"name": "אור בן הרוש דרום", "email": "sor.benharush@examplexyz.com"},
    {"name": "דפנה ברק דרום", "email": "sdafna.barak@examplexyz.com"},
    {"name": "ירון לוי דרום", "email": "syaron.levy@examplexyz.com"},
    {"name": "שי נמרוד דרום", "email": "sshay.nimrod@examplexyz.com"},
    {"name": "הדר מימון דרום", "email": "shadar.maimon@examplexyz.com"},
    {"name": "ניצן כרמי דרום", "email": "snitzan.karmi@examplexyz.com"},
    {"name": "אופיר קרן דרום", "email": "sofir.keren@examplexyz.com"},
    {"name": "דקלה ארנון דרום", "email": "sdikla.arnon@examplexyz.com"},
    {"name": "מתן רום דרום", "email": "smatan.rom@examplexyz.com"},
    {"name": "רותם דיין דרום", "email": "srotem.dayan@examplexyz.com"},
]
usernames = [user["name"] for user in users_list]


module_name = "קול התושבים"
module_desc = "מודול זה מאפשר לכל תושבי הישוב להוסיף רעיונות לפרויקטים עירוניים, להצביע לרעיונות שהוצעו על ידי אחרים, ולבסוף לקבלת הרעיונות על ידי חברי המועצה. המודול יוצר הזדמנות שווה והוגנת לקבלת רעיונות מכל הקהילות, תוך מתן עדיפות לרעיונות מקהילות שפרויקטים שלהן לא התקבלו בעבר, כך שיוכלו לקבל סיכוי גבוה יותר להיבחר בעתיד."
project_name = "פרויקטים עירוניים"
project_desc = "סדרת יוזמות ופיתוחים מקומיים שמטרתם לשפר את איכות החיים, להגביר את הקהילתיות ולתמוך בסביבה. הפרויקטים כוללים שיפוץ ושדרוג מתקנים קיימים, הקמת תשתיות חדשות וקידום יוזמות חינוכיות, תרבותיות וסביבתיות לטובת כלל התושבים."
org_name = "מועצת פרדס חנה"
superuser_name = "יושב ראש המועצה"
users_obj = [User.objects.get(username=name) for name in usernames]

ideavs= IdeaChoinViewSet()

class fairVoteSNTestCase():

    def setUp(self):
        """
        here we created a new db by running: python manage.py test apps.fairvote.tests.fairVoteTestCase
        """
        email = 'chairman@example.com'
        superuser = User.objects.create(username=superuser_name,email=email)
        superuser.set_password("password")
        superuser.is_superuser = True
        superuser.is_staff = True
        superuser.save()
        EmailAddress.objects.create(user=superuser,email=email,verified=True)
        
        org, org_created = Organisation.objects.get_or_create(name=org_name,defaults={"name":org_name})
        logger.info("org: %s, created: %s", org, org_created)
        if org_created:
            org.initiators.set([User.objects.get(username=superuser_name)])
            
        project, project_created = Project.objects.get_or_create(
                                                name=project_name,
                                                organisation=org,
                                                defaults={"description": project_desc, "is_draft": False,
                                                           "name": project_name, "organisation": org,
                                                           "access": Access.SEMIPUBLIC}
                                            )
        logger.info("project: %s, created: %s", project, project_created)

        from datetime import datetime
        module, module_created = Module.objects.get_or_create(name=module_name, project=project,
                                                               defaults={"name":module_name,"project":project,
                                                                         "description":module_desc,
                                                                         "blueprint_type":"FV","weight":0})
        logger.info("module: %s, created: %s", module, module_created)

        if module_created:
            fv = FairVotePhase()
            Phase.objects.create(module=module, name=fv.name, description= fv.description,
                                type=fv.identifier,start_date=datetime.now(),
                                    end_date= datetime.now().replace(year=datetime.now().year+1))
        
        for user in users_list:
            username=user['name']
            email=user['email']
            user_obj= User.objects.create(username=username,email=email,language='en')
            logger.info("user: %s" , user_obj )

            user_obj.set_password("password")
            user_obj.save()
            users_obj.append(user_obj)
            EmailAddress.objects.create(user=user_obj,email=email,verified=True)
            OrganisationTermsOfUse.objects.create(user=user, organisation=org, has_agreed=True)
            project.participants.add(user_obj)

            # automatic
            #choin = Choin.objects.create(user=user_obj, module=module)
            #logger.info("user choins: %s", choin )
        

    def get_module(self):
        module = Module.objects.get(name=module_name, project__name=project_name, project__organisation__name=org_name)
        logger.info("module: %s", module)
        return module

    def create_idea(self, module: Module, idea_title, idea_desc, idea_creator, idea_goal):
        # use IdeaForm instead of creating and check 
        idea = Idea.objects.create(module=module, name=idea_title, description=idea_desc, creator=idea_creator)
        
        idea_choin, created = IdeaChoin.objects.get_or_create(idea=idea,defaults={"idea":idea, "goal": idea_goal})
        logger.info("idea: %s, idea choin: %s", idea, idea_choin)
        return idea, idea_choin

    def create_idea_use_form(self, module: Module, idea_title, idea_desc, idea_creator, idea_goal):
        # use IdeaForm instead of creating and check 
        agreed,a_created = OrganisationTermsOfUse.objects.get_or_create(user=idea_creator,
                                                                        organisation=module.project.organisation,
                                                                        defaults={
                                                                            "organisation": module.project.organisation,
                                                                            "user": idea_creator,
                                                                            "has_agreed":True
                                                                            })
        
        form_data = {
            'name': idea_title,
            'description': idea_desc,
            'organisation_terms_of_use':True
        }
        form = IdeaForm(data=form_data, module=module, user=idea_creator,)
        if not form.is_valid():
            print(form.errors)
            raise Exception("idea form isn't valid:")
        idea = form.save(commit=False)
        idea.creator = idea_creator
        idea.module = module
        #form.save()
        idea.save()
        
        idea_choin, created = IdeaChoin.objects.get_or_create(idea=idea,defaults={"idea":idea, "goal": idea_goal})
        if not created:
            logger.info("WARNING: idea choin wasn't create by idea form")
        logger.info("idea: %s, idea choin: %s", idea, idea_choin)
        return idea, idea_choin


    def vote_idea(self,users, idea, idea_choin):
        users_choin = Choin.objects.filter(module=idea.module, user__in=users)
        content_type = ContentType.objects.get_for_model(Idea)
        logger.info("users choins: %s", users_choin)

        for user in users:
            contenttype = ContentType.objects.get_for_model(idea)
            permission = "{ct.app_label}.rate_{ct.model}".format(ct=contenttype)
            has_rate_permission = user.has_perm(permission, idea)
            would_have_rate_permission = NormalUser().would_have_perm(permission, idea)

            if has_rate_permission or would_have_rate_permission:
                logger.info("user %s has rate permission", user)

                # idea_choins = idea_choin.choins
                rating, created = Rating.objects.get_or_create(
                    creator=user,
                    content_type=content_type,
                    object_pk=idea.pk,
                    defaults={"creator": user, "content_type":content_type, 
                            "object_pk": idea.pk, "value":1 }
                )
                logger.info("2. rating: %s,%s,%s, created: %s",rating.idea, rating.creator, rating.value, created)
                
                #user_choin = Choin.objects.filter(user=user).first()
                #user_choin_before = 0
                #if user_choin is not None:
                #    user_choin_before = user_choin.choins

                # update user and idea choins and check if they updated as excpted
                request = HttpRequest()
                request.user = user
                data = {
                    "value": 1,
                    "ideaId": idea.pk,
                }
                request.data = data
                ideavs.update_idea_choins_at_user_first_rating(request)
                idea_choin.refresh_from_db()
            else:
                logger.info("user %s has no rate permission", user)

    def check_supporters(self, users, updated_choins):
        if updated_choins:
            for user,user_choin in zip(users, updated_choins):
                choins_from_db=Choin.objects.get(user=user).choins
                logger.info("user: %s, choins from db: %s, expected: %s", user,choins_from_db, user_choin)
        else:
            for user in users:
                choins_from_db=Choin.objects.get(user=user).choins
                logger.info("user: %s, choins from db: %s, expected: %s", user, choins_from_db, 0)

    def check_not_supporters(self, users_dont_support, giveaway = 0):
        for user, choins in users_dont_support.items():
            choins_from_db= Choin.objects.get(user=user).choins
            expected_choins = choins + giveaway
            logger.info("user: %s, choins from db: %s, origin+giveaway = %s", user ,choins_from_db, 
                       expected_choins)

    def accept_idea(self, idea):
        # accept idea by using idea moderation form
        form_data = {
            "moderator_status": "ACCEPTED"
        }
        idea_accept_form = IdeaModerateForm(data=form_data, instance=idea)
        idea_accept_form.save()
    
    def rating_changing(self,idea,idea_choin, ideavs):
        # choins_before = idea_choin.choins
        ratings = idea.ratings.all()
        for rating in ratings:
            request = HttpRequest()
            request.user = rating.creator
            rating_prev_val = rating.value
            rating.value = 0
            rating.save()
            data = {
                "oldValue": rating_prev_val,
                "newValue": rating.value,
                "positiveRatings": ratings.count()-1,
                "ideaId": idea.pk,
            }
            request.data = data
            # user_choins = Choin.objects.get(user=rating.creator).choins
            ideavs.update_idea_choins_at_user_rating_update(request)
            idea_choin.refresh_from_db()
            rating_prev_val = rating.value
            rating.value = 1
            rating.save()

            data = {
                "oldValue": rating_prev_val,
                "newValue": rating.value,
                "positiveRatings": ratings.count(),
                "ideaId": idea.pk,
            }
            request.data = data
            ideavs.update_idea_choins_at_user_rating_update(request)
            idea_choin.refresh_from_db()


    def test_fairvote(self,users,choins,idea: Idea, idea_choin, giveaway=0, updated_choins= None):
        logger.info("test-fairvote")
        
        # init user choins
        for user,user_choin in zip(users, choins):
            choin, choin_created = Choin.objects.get_or_create(user=user,module=idea.module)
            if choin_created:
                logger.info("WARNING: %s created independntly", choin)
            choin.choins=user_choin
            choin.save()
            logger.info("1. user choins: %s", choin )


        # create ratings
        self.vote_idea(users,idea,idea_choin)

        users_dont_support = {user_choin.user: user_choin.choins for user_choin in
                               Choin.objects.filter(module=idea.module).exclude(user__in=users)}
        logger.info("users dont support choins: %s", users_dont_support)
        
        idea_choin.refresh_from_db()
        
        # check idea choins:
        
        self.rating_changing(idea,idea_choin, ideavs)
        
        # accept idea by using idea moderation form
        self.accept_idea(idea)
        
        # check user choins after accept idea
        # supporters:
        self.check_supporters(users,updated_choins)
        
        # not-supporters
        self.check_not_supporters(users_dont_support,giveaway)


    def test_greater_than_goal_2(self):
        
        choins = [5,20,20]

        idea_title = "idea_gtg"
        idea_desc = "desc"
        idea_creator = User.objects.get(username=superuser_name)
        idea_goal = 40
        choins_sum = sum(choins)
        choins_to_divide = idea_goal/choins_sum  
        updated_choins = [user_choins-(user_choins*choins_to_divide) for user_choins in choins]
        module = self.get_module()
        idea,idea_choin = self.create_idea(module,idea_title, idea_desc, idea_creator, idea_goal)
        self.test_fairvote(users_obj[:3],choins,idea, idea_choin,updated_choins=updated_choins)

    def test_sn_users(self):
        # 3 north, 5 south: 0 choins
        # 8 ideas- 5s, 3n
        # s,s,n,s,s,n
        import random
        module = self.get_module()
        def create_ideas(a,b,label):
            ideas = []
            for idea in idea_list[a:b]:
                idea_title = idea["name"]
                idea_desc = idea["description"]
                idea_goal = random.randint(1000,2000)
                idea_creator =users_obj[random.randint(0,16)] if label=="n" else users_obj[random.randint(16,40)]
                idea_tuple = self.create_idea_use_form(module,idea_title,idea_desc,idea_creator,idea_goal)
                ideas.append(idea_tuple)
            return ideas
        
        def vote_ideas(users, ideas):
            for (idea,idea_choin) in ideas:
                logger.info("users vote for: %s - %s", idea, idea_choin.choins)
                self.vote_idea(users,idea,idea_choin)
                logger.info("missing: %s", idea_choin.missing )

        Idea.objects.filter(module=module).delete()
        north_ideas = create_ideas(0,20,"n")
        logger.info("north ideas: %s", north_ideas)
        south_ideas = create_ideas(20,40,"s")
        logger.info("south ideas: %s", south_ideas)
        ideas = Idea.objects.filter(module=module).order_by("created")
        north_ideas = ideas[:20]
        north_ideas = [(idea,IdeaChoin.objects.get(idea=idea)) for idea in north_ideas]
        south_ideas = ideas[20:]
        south_ideas = [(idea,IdeaChoin.objects.get(idea=idea)) for idea in south_ideas]
        vote_ideas(users_obj[:16],north_ideas)
        vote_ideas(users_obj[16:40],south_ideas)
        update_ideas_acceptance_order(module.pk)
        fair_ideas = IdeaChoin.objects.filter(idea__module=module).order_by("order")
        for idea in fair_ideas:
            logger.info("%s. idea: %s, missing: %s", idea.order,idea.idea.name,idea.missing)

if __name__=='__main__':
   test= fairVoteSNTestCase()
   test.test_sn_users()