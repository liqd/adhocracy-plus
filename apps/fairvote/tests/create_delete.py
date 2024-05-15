import os

import django
from allauth.account.models import EmailAddress

from adhocracy4.modules.models import Module
from adhocracy4.phases.models import Phase
from adhocracy4.ratings.models import Rating
from apps.fairvote.models import Choin
from apps.fairvote.models import ChoinEvent
from apps.fairvote.models import Idea
from apps.fairvote.models import IdeaChoin
from apps.fairvote.models import UserIdeaChoin
from apps.fairvote.phases import FairVotePhase
from apps.organisations.models import Organisation
from apps.projects.models import Project
from apps.users.models import User

# Configure Django environment **SHOULD BE AFTER IMPORT os, django**
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "adhocracy-plus.config.settings")
django.setup()

user_list = [
    {"name": "SouthAlexTurner", "email": "salex.turner@examplexyz.com"},
    {"name": "SouthEmilyBennett", "email": "semily.bennett@examplexyz.com"},
    {"name": "SouthDanielMitchell", "email": "sdaniel.mitchell@examplexyz.com"},
    {"name": "SouthOliviaReynolds", "email": "solivia.reynolds@examplexyz.com"},
    {"name": "SouthEthanLawson", "email": "sethan.lawson@examplexyz.com"},
    {"name": "SouthSophiaChambers", "email": "ssophia.chambers@examplexyz.com"},
    {"name": "SouthLiamHarrison", "email": "sliam.harrison@examplexyz.com"},
    {"name": "SouthAvaSullivan", "email": "sava.sullivan@examplexyz.com"},
    {"name": "SouthNoahBrooks", "email": "snoah.brooks@examplexyz.com"},
    {"name": "SouthMiaLawrence", "email": "smia.lawrence@examplexyz.com"},
    {"name": "SouthBenjaminFoster", "email": "sbenjamin.foster@examplexyz.com"},
    {"name": "SouthChloeMorgan", "email": "schloe.morgan@examplexyz.com"},
    {"name": "SouthSamuelHayes", "email": "ssamuel.hayes@examplexyz.com"},
    {"name": "SouthLilyColeman", "email": "slily.coleman@examplexyz.com"},
    {"name": "SouthIsaacSimmons", "email": "sisaac.simmons@examplexyz.com"},
    {"name": "SouthGracePalmer", "email": "sgrace.palmer@examplexyz.com"},
    {"name": "SouthHenryWallace", "email": "shenry.wallace@examplexyz.com"},
    {"name": "SouthScarlettDavis", "email": "sscarlett.davis@examplexyz.com"},
    {"name": "SouthLucasParker", "email": "slucas.parker@examplexyz.com"},
    {"name": "SouthAmeliaKnight", "email": "samelia.knight@examplexyz.com"},
    {"name": "SouthBellaDavid", "email": "sbella.david@examplexyz.com"},
    {"name": "SouthEmmaStein", "email": "semma.stein@examplexyz.com"},
    {"name": "SouthDanielLightman", "email": "sdaniel.lightman@examplexyz.com"},
    {"name": "SouthTanyaSpeiser", "email": "stanya.speiser@examplexyz.com"},
    {"name": "NorthEthanLawson", "email": "nethan.lawson@examplexyz.com"},
    {"name": "NorthSophiaChambers", "email": "nsophia.chambers@examplexyz.com"},
    {"name": "NorthLiamHarrison", "email": "nliam.harrison@examplexyz.com"},
    {"name": "NorthAvaSullivan", "email": "nava.sullivan@examplexyz.com"},
    {"name": "NorthNoahBrooks", "email": "nnoah.brooks@examplexyz.com"},
    {"name": "NorthMiaLawrence", "email": "nmia.lawrence@examplexyz.com"},
    {"name": "NorthBenjaminFoster", "email": "nbenjamin.foster@examplexyz.com"},
    {"name": "NorthChloeMorgan", "email": "nchloe.morgan@examplexyz.com"},
    {"name": "NorthSamuelHayes", "email": "nsamuel.hayes@examplexyz.com"},
    {"name": "NorthLilyColeman", "email": "nlily.coleman@examplexyz.com"},
    {"name": "NorthIsaacSimmons", "email": "nisaac.simmons@examplexyz.com"},
    {"name": "NorthGracePalmer", "email": "ngrace.palmer@examplexyz.com"},
    {"name": "NorthHenryWallace", "email": "nhenry.wallace@examplexyz.com"},
    {"name": "NorthScarlettDavis", "email": "nscarlett.davis@examplexyz.com"},
    {"name": "NorthLucasParker", "email": "nlucas.parker@examplexyz.com"},
    {"name": "NorthAmeliaKnight", "email": "namelia.knight@examplexyz.com"},
]

usernames = [user["name"] for user in user_list]

ORG = "SN Org"
PROJECT = "South-North Projects"
MODULE = "South-North Module"
superuser_name = "superuser"
superuser_pass = "password"


def create_superuser(name=superuser_name, password=superuser_pass):
    email = f"{name}@csriel.xyz"
    superuser = User.objects.create(username=name, email=email)
    superuser.set_password(password)
    superuser.is_superuser = True
    superuser.is_staff = True
    superuser.save()
    EmailAddress.objects.create(user=superuser, email=email, verified=True)
    return superuser


def create_organisation(initiator, name=ORG):
    org = Organisation.objects.create(name=name)
    org.initiators.set([initiator])
    return org


def create_project(org, name=PROJECT):
    project = Project.objects.create(
        name=name, organisation=org, description="desc", is_draft=False
    )
    return project


def create_module(project, name=MODULE):
    from datetime import datetime

    module = Module.objects.create(
        name=name, project=project, description="desc", blueprint_type="FV", weight=0
    )
    fv = FairVotePhase()
    Phase.objects.create(
        module=module,
        name=fv.name,
        description=fv.description,
        type=fv.identifier,
        start_date=datetime.now(),
        end_date=datetime.now().replace(year=datetime.now().year + 1),
    )


def register():
    for user in user_list:
        username = user["name"]
        email = user["email"]
        # print(username,email,password)
        user_obj = User.objects.create(username=username, email=email, language="en")
        user_obj.set_password("password")
        user_obj.save()
        EmailAddress.objects.create(user=user_obj, email=email, verified=True)


def delete_users():
    """
    delete all users in `user_list`.
    """
    User.objects.filter(username__in=usernames).delete()
    print("delete_users")


def delete_org():
    """ "
    delete organisation
    """
    Organisation.objects.get(name=ORG).delete()


def delete_ideas():
    """
    delete ideas
    """
    Idea.objects.filter(module__name=MODULE, module__project__name=PROJECT).delete()


def delete_ratings():
    """
    delete ratings
    """
    print(Rating.objects.filter(idea__module__project__name=PROJECT).delete())


def delete_all():
    """
    delete all relevant data (all depend on org and users)
    """
    delete_org()
    delete_users()


def reset_users_choins():
    """
    update all users choins to 0
    """
    Choin.objects.update(choins=0)


def delete_users_choins():
    """
    delete all users choins
    """
    Choin.objects.all().delete()


def reset_idea_choins():
    """
    update all ideas to be with 0 choins and 150 missing choins.
    """
    IdeaChoin.objects.update(choins=0, missing=150)
    print("reset_idea_choins")


def update_missing_choins():
    """
    update all ideas with 0 missing choins to 150 missing choins.
    """
    IdeaChoin.objects.filter(missing=0.0).update(missing=150.0)


def unaccept_all_ideas():
    """
    reset all ideas status
    """
    Idea.objects.filter(module__name=MODULE, module__project__name=PROJECT).update(
        moderator_status=""
    )


def delete_users_invest_records():
    """
    delete users "paid" for ideas records
    """
    UserIdeaChoin.objects.filter(idea__module__project__name=PROJECT).delete()


def delete_choin_events():
    ChoinEvent.objects.all().delete()
    print("delete_choin_events")


def reset_as_before_votes():
    """
    keep users and ideas(including porject and organization)
    delete votes and choins of users and ideas.
    """
    delete_ratings()
    reset_idea_choins()
    # reset_users_choins()
    delete_users_choins()
    delete_choin_events()
    unaccept_all_ideas()
    delete_users_invest_records()


if __name__ == "__main__":
    # create_superuser()
    # superuser= create_superuser()

    # superuser = User.objects.get(username=superuser_name)

    # org = create_organisation(superuser)
    # org = Organisation.objects.get(name=ORG)
    # proj = create_project(org)
    # create_module(proj)
    # register()
    # delete_users()
    # update_missing_choins()
    # reset_as_before_votes()
    pass
