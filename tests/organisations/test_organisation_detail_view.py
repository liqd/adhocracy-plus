import pytest
from dateutil.parser import parse
from django.urls import reverse
from freezegun import freeze_time

from adhocracy4.projects.enums import Access


@pytest.mark.django_db
def test_hide_private_projects(client, user, project_factory,
                               module_factory, phase_factory, organisation):
    public = project_factory(organisation=organisation)
    semipublic = project_factory(access=Access.SEMIPUBLIC,
                                 organisation=organisation)
    private = project_factory(access=Access.PRIVATE, organisation=organisation)

    module1 = module_factory(project=public, weight=1)
    module2 = module_factory(project=semipublic, weight=2)
    module3 = module_factory(project=private, weight=3)

    phase_factory(
        module=module1,
        start_date=parse('2013-01-01 17:10:00 UTC'),
        end_date=parse('2013-01-01 18:05:00 UTC'),
    )

    phase_factory(
        module=module2,
        start_date=parse('2013-01-01 17:05:00 UTC'),
        end_date=parse('2013-01-01 19:00:00 UTC')
    )

    phase_factory(
        module=module3,
        start_date=parse('2013-01-01 17:15:00 UTC'),
        end_date=parse('2013-01-01 19:05:00 UTC')
    )

    with freeze_time(parse('2013-01-01 18:00:00 UTC')):
        client.login(username=user, password='password')
        url = reverse('organisation',
                      kwargs={'organisation_slug': organisation.slug})
        response = client.get(url)
        assert response.status_code == 200

        project_list = response.context['active_projects']
        project_headline = response.context['project_headline']
        assert public in project_list
        assert semipublic in project_list
        assert private not in project_list
        assert project_headline == 'Participate now!'


@pytest.mark.django_db
def test_show_private_projects_participant(client, user, project_factory,
                                           module_factory, phase_factory,
                                           organisation):

    public = project_factory(organisation=organisation)
    semipublic = project_factory(access=Access.SEMIPUBLIC,
                                 organisation=organisation)
    private = project_factory(access=Access.PRIVATE, organisation=organisation)
    private.participants.add(user)

    module1 = module_factory(project=public, weight=1)
    module2 = module_factory(project=semipublic, weight=2)
    module3 = module_factory(project=private, weight=3)

    phase_factory(
        module=module1,
        start_date=parse('2013-01-01 17:10:00 UTC'),
        end_date=parse('2013-01-01 18:05:00 UTC'),
    )

    phase_factory(
        module=module2,
        start_date=parse('2013-01-01 17:05:00 UTC'),
        end_date=parse('2013-01-01 19:00:00 UTC')
    )

    phase_factory(
        module=module3,
        start_date=parse('2013-01-01 17:00:00 UTC'),
        end_date=parse('2013-01-01 18:30:00 UTC')
    )

    with freeze_time(parse('2013-01-01 19:05:00 UTC')):
        client.login(username=user, password='password')
        url = reverse('organisation',
                      kwargs={'organisation_slug': organisation.slug})
        response = client.get(url)
        assert response.status_code == 200

        past_projects = response.context['past_projects']
        project_headline = response.context['project_headline']
        assert public in past_projects
        assert semipublic in past_projects
        assert private in past_projects
        assert project_headline == 'Ended participation'


@pytest.mark.django_db
def test_show_private_projects_initiators(client, user, project_factory,
                                          module_factory, phase_factory,
                                          organisation):

    public = project_factory(organisation=organisation)
    semipublic = project_factory(access=Access.SEMIPUBLIC,
                                 organisation=organisation)
    private = project_factory(access=Access.PRIVATE, organisation=organisation)
    private.organisation.initiators.add(user)

    module1 = module_factory(project=public, weight=1)
    module2 = module_factory(project=semipublic, weight=2)
    module3 = module_factory(project=private, weight=3)

    phase_factory(
        module=module1,
        start_date=parse('2013-01-01 17:10:00 UTC'),
        end_date=parse('2013-01-01 18:05:00 UTC'),
    )

    phase_factory(
        module=module2,
        start_date=parse('2013-01-01 16:00:00 UTC'),
        end_date=parse('2013-01-01 16:30:00 UTC')
    )

    phase_factory(
        module=module3,
        start_date=parse('2013-01-01 17:05:00 UTC'),
        end_date=parse('2013-01-01 19:00:00 UTC')
    )

    with freeze_time(parse('2013-01-01 17:00:00 UTC')):
        client.login(username=user, password='password')
        url = reverse('organisation',
                      kwargs={'organisation_slug': organisation.slug})
        response = client.get(url)
        assert response.status_code == 200

        future_projects = response.context['future_projects']
        past_projects = response.context['past_projects']
        project_headline = response.context['project_headline']
        assert public in future_projects
        assert semipublic in past_projects
        assert private in future_projects
        assert project_headline == 'Upcoming participation'


@pytest.mark.django_db
def test_show_private_projects_members(client, member, project_factory,
                                       module_factory, phase_factory):
    organisation = member.organisation
    public = project_factory(organisation=organisation)
    semipublic = project_factory(access=Access.SEMIPUBLIC,
                                 organisation=organisation)
    private = project_factory(access=Access.PRIVATE, organisation=organisation)

    module1 = module_factory(project=public, weight=1)
    module2 = module_factory(project=semipublic, weight=2)
    module3 = module_factory(project=private, weight=3)

    phase_factory(
        module=module1,
        start_date=parse('2013-01-01 17:10:00 UTC'),
        end_date=parse('2013-01-01 18:05:00 UTC'),
    )

    phase_factory(
        module=module2,
        start_date=parse('2013-01-01 16:00:00 UTC'),
        end_date=parse('2013-01-01 16:30:00 UTC')
    )

    phase_factory(
        module=module3,
        start_date=parse('2013-01-01 17:05:00 UTC'),
        end_date=parse('2013-01-01 19:00:00 UTC')
    )

    with freeze_time(parse('2013-01-01 17:07:00 UTC')):
        client.login(username=member.member, password='password')
        url = reverse('organisation',
                      kwargs={'organisation_slug': organisation.slug})
        response = client.get(url)
        assert response.status_code == 200

        active_projects = response.context['active_projects']
        future_projects = response.context['future_projects']
        past_projects = response.context['past_projects']
        project_headline = response.context['project_headline']
        assert public not in active_projects
        assert semipublic not in active_projects
        assert private in active_projects
        assert public in future_projects
        assert semipublic not in future_projects
        assert private not in future_projects
        assert public not in past_projects
        assert semipublic in past_projects
        assert private not in past_projects
        assert project_headline == 'Participate now!'
