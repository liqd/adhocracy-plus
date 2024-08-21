from allauth.account.models import EmailAddress
from django.test import TestCase
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
from apps.fairvote.algorithms import fair_acceptance_order
import logging
logger = logging.getLogger(__name__)
"""
1. submit idea
2. all users vote for it
3. check the idea choins, and missing
4. accept idea
5. check users balance - including not supporting users
6. optional: check other ideas choins
"""

users_list = [{"name":"suser1","email":"suser1@example.com"},
                {"name":"suser2","email":"suser2@example.com"},
                {"name":"suser3","email":"suser3@example.com"},
                {"name":"suser4","email":"suser4@example.com"},
                {"name":"suser5","email":"suser5@example.com"},
                {"name":"nuser1","email":"nuser1@example.com"},
                {"name":"nuser2","email":"nuser2@example.com"},
                {"name":"nuser3","email":"nuser3@example.com"},]

module_name = "fvtest-sn-module"
project_name = "fvtest-sn-project"
org_name = "fvtest-sn-org"

"""
users_list = [{"name":"user1","email":"user1@example.com"},
              {"name":"user2","email":"user2@example.com"},
              {"name":"user3","email":"user3@example.com"},
              {"name":"user4","email":"user4@example.com"},
              {"name":"user5","email":"user5@example.com"}]
module_name = "fvtest-module"
project_name = "fvtest-project"
org_name = "fvtest-org"
"""

users_obj = []
ideavs = IdeaChoinViewSet()

class fairVoteSNTestCase(TestCase):
    def setUp(self):
        """
        here we created a new db by running: python manage.py test apps.fairvote.tests.fairVoteTestCase
        """
        email = 'superuser@example.com'
        superuser = User.objects.create(username="superuser",email=email)
        superuser.set_password("password")
        superuser.is_superuser = True
        superuser.is_staff = True
        superuser.save()
        EmailAddress.objects.create(user=superuser,email=email,verified=True)
        
        org, org_created = Organisation.objects.get_or_create(defaults={"name":org_name})
        logger.info("org: %s, created: %s", org, org_created)
        if org_created:
            org.initiators.set([User.objects.get(username='superuser')])
            
        project, project_created = Project.objects.get_or_create(
                                                name=project_name,
                                                organisation=org,
                                                defaults={"description": "desc", "is_draft": False,
                                                           "name": project_name, "organisation": org,
                                                           "access": Access.SEMIPUBLIC}
                                            )
        logger.info("project: %s, created: %s", project, project_created)

        from datetime import datetime
        module, module_created = Module.objects.get_or_create(name=module_name, project=project,
                                                               defaults={"name":module_name,"project":project,
                                                                         "description":"desc",
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
            logger.info("user: %s" , user_obj)

            user_obj.set_password("password")
            user_obj.save()
            users_obj.append(user_obj)
            EmailAddress.objects.create(user=user_obj,email=email,verified=True)
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
        form_data = {
            'name': idea_title,
            'description': idea_desc,
            'organisation_terms_of_use':True,
            'goal': idea_goal
        }
        form = IdeaForm(data=form_data, module=module, user=idea_creator)
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

                idea_choins = idea_choin.choins
                rating, created = Rating.objects.get_or_create(
                    creator=user,
                    content_type=content_type,
                    object_pk=idea.pk,
                    defaults={"creator": user, "content_type":content_type, 
                            "object_pk": idea.pk, "value":1 }
                )
                logger.info("2. rating: %s,%s,%s, created: %s",rating.idea, rating.creator, rating.value, created)
                
                user_choin = Choin.objects.filter(user=user).first()
                user_choin_before = 0
                if user_choin is not None:
                    user_choin_before = user_choin.choins

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
                self.assertAlmostEqual(idea_choin.choins,idea_choins+user_choin_before)
            else:
                logger.info("user %s has no rate permission", user)

    def check_supporters(self, users, updated_choins):
        if updated_choins:
            for user,user_choin in zip(users, updated_choins):
                choins_from_db=Choin.objects.get(user=user).choins
                logger.info("user: %s, choins from db: %s, expected: %s", user,choins_from_db, user_choin)
                self.assertAlmostEqual(choins_from_db, user_choin)
        else:
            for user in users:
                choins_from_db=Choin.objects.get(user=user).choins
                logger.info("user: %s, choins from db: %s, expected: %s", user, choins_from_db, 0)
                self.assertEqual(choins_from_db, 0)

    def check_not_supporters(self, users_dont_support, giveaway = 0):
        for user, choins in users_dont_support.items():
            choins_from_db= Choin.objects.get(user=user).choins
            expected_choins = choins + giveaway
            logger.info("user: %s, choins from db: %s, origin+giveaway = %s", user ,choins_from_db, 
                       expected_choins)
            self.assertAlmostEqual(expected_choins, choins_from_db)

    def accept_idea(self, idea):
        # accept idea by using idea moderation form
        form_data = {
            "moderator_status": "ACCEPTED"
        }
        idea_accept_form = IdeaModerateForm(data=form_data, instance=idea)
        idea_accept_form.save()
    
    def rating_changing(self,idea,idea_choin, ideavs):
        choins_before = idea_choin.choins
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
            user_choins = Choin.objects.get(user=rating.creator).choins
            ideavs.update_idea_choins_at_user_rating_update(request)
            idea_choin.refresh_from_db()
            rating_prev_val = rating.value
            rating.value = 1
            rating.save()

            self.assertAlmostEqual(choins_before-user_choins,idea_choin.choins)
            data = {
                "oldValue": rating_prev_val,
                "newValue": rating.value,
                "positiveRatings": ratings.count(),
                "ideaId": idea.pk,
            }
            request.data = data
            ideavs.update_idea_choins_at_user_rating_update(request)
            idea_choin.refresh_from_db()
            self.assertAlmostEqual(choins_before,idea_choin.choins)


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
        self.assertAlmostEqual(idea_choin.choins, sum(choins))
        
        self.rating_changing(idea,idea_choin, ideavs)
        
        # accept idea by using idea moderation form
        self.accept_idea(idea)
        
        # check user choins after accept idea
        # supporters:
        self.check_supporters(users,updated_choins)
        
        # not-supporters
        self.check_not_supporters(users_dont_support,giveaway)

    def test_less_than_goal(self):

        choins = [5,10,15]

        idea_title = "idea_ltg"
        idea_desc = "desc"
        idea_creator = User.objects.get(username="superuser")
        idea_goal = 40
        
        module = self.get_module()
        idea,idea_choin = self.create_idea(module,idea_title, idea_desc, idea_creator, idea_goal)
        giveway = (idea_goal - sum(choins))/len(choins)
        self.test_fairvote(users_obj[:3],choins,idea,idea_choin,giveaway=giveway)

    def test_equal_to_goal(self):
        
        choins = [10,15,15]

        idea_title = "idea_etg"
        idea_desc = "desc"
        idea_creator = User.objects.get(username="superuser")
        idea_goal = 40
        
        module = self.get_module()
        idea,idea_choin = self.create_idea_use_form(module,idea_title, idea_desc, idea_creator, idea_goal)
        self.test_fairvote(users_obj[:3],choins,idea, idea_choin)


    def test_greater_than_goal(self):
        
        choins = [10,15,20]

        idea_title = "idea_gtg"
        idea_desc = "desc"
        idea_creator = User.objects.get(username="superuser")
        idea_goal = 40
        choins_sum = sum(choins)
        choins_to_divide = idea_goal/choins_sum
        updated_choins = [user_choins-(user_choins*choins_to_divide) for user_choins in choins]
        module = self.get_module()
        idea,idea_choin = self.create_idea_use_form(module,idea_title, idea_desc, idea_creator, idea_goal)
        self.test_fairvote(users_obj[:3],choins,idea, idea_choin,updated_choins=updated_choins)


    def test_greater_than_goal_2(self):
        
        choins = [5,20,20]

        idea_title = "idea_gtg"
        idea_desc = "desc"
        idea_creator = User.objects.get(username="superuser")
        idea_goal = 40
        choins_sum = sum(choins)
        choins_to_divide = idea_goal/choins_sum
        updated_choins = [user_choins-(user_choins*choins_to_divide) for user_choins in choins]
        module = self.get_module()
        idea,idea_choin = self.create_idea_use_form(module,idea_title, idea_desc, idea_creator, idea_goal)
        self.test_fairvote(users_obj[:3],choins,idea, idea_choin,updated_choins=updated_choins)

    def test_sn_users(self):
        # 3 north, 5 south: 0 choins
        # 8 ideas- 5s, 3n
        # s,s,n,s,s,n
        module = self.get_module()
        idea_creator = User.objects.get(username="superuser")
        idea_desc = "desc"
        idea_goal = 100

        def create_ideas(n, label):
            ideas = []
            for i in range(1,n+1):
                idea_title = f"{label}_idea_{i}"
                idea_tuple = self.create_idea_use_form(module,idea_title,idea_desc,idea_creator,idea_goal)
                ideas.append(idea_tuple)
            return ideas
        
        def vote_ideas(users, ideas):
            for (idea,idea_choin) in ideas:
                logger.info("users vote for: %s - %s", idea, idea_choin.choins)
                self.vote_idea(users,idea,idea_choin)
                logger.info("missing: %s", idea_choin.missing )

        south_users = users_obj[:5]
        north_users = users_obj[5:]
        south_ideas = create_ideas(5,"south")
        logger.info("south ideas: %s", south_ideas)
        north_ideas = create_ideas(3,"north")
        logger.info("north ideas: %s", north_ideas)
        vote_ideas(south_users,south_ideas)
        vote_ideas(north_users,north_ideas)
        fair_acceptance_order(module.pk,top=8)
        fair_ideas = IdeaChoin.objects.filter(idea__module=module).order_by("order")
        print(fair_ideas)