import pytest
from dateutil.parser import parse
from django.urls import reverse
from freezegun import freeze_time


@pytest.mark.django_db
def test_hide_private_projects(client, user, project_factory,
                               module_factory, phase_factory, organisation):
    public = project_factory(organisation=organisation)
    private = project_factory(is_public=False, organisation=organisation)

    module1 = module_factory(project=public, weight=1)
    module2 = module_factory(project=private, weight=2)

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

    with freeze_time(parse('2013-01-01 18:00:00 UTC')):
        client.login(username=user, password='password')
        url = reverse('organisation',
                      kwargs={'organisation_slug': organisation.slug})
        response = client.get(url)
        assert response.status_code == 200

        project_list = response.context['active_projects']
        assert public in project_list
        assert private not in project_list


@pytest.mark.django_db
def test_show_private_projects_participant(client, user, project_factory,
                                           module_factory, phase_factory,
                                           organisation):

    public = project_factory(organisation=organisation)
    private = project_factory(is_public=False, organisation=organisation)
    private.participants.add(user)

    module1 = module_factory(project=public, weight=1)
    module2 = module_factory(project=private, weight=2)

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

    with freeze_time(parse('2013-01-01 18:00:00 UTC')):
        client.login(username=user, password='password')
        url = reverse('organisation',
                      kwargs={'organisation_slug': organisation.slug})
        response = client.get(url)
        assert response.status_code == 200

        project_list = response.context['active_projects']
        assert public in project_list
        assert private in project_list


@pytest.mark.django_db
def test_show_private_projects_initiators(client, user, project_factory,
                                          module_factory, phase_factory,
                                          organisation):

    public = project_factory(organisation=organisation)
    private = project_factory(is_public=False, organisation=organisation)
    private.organisation.initiators.add(user)

    module1 = module_factory(project=public, weight=1)
    module2 = module_factory(project=private, weight=2)

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

    with freeze_time(parse('2013-01-01 18:00:00 UTC')):
        client.login(username=user, password='password')
        url = reverse('organisation',
                      kwargs={'organisation_slug': organisation.slug})
        response = client.get(url)
        assert response.status_code == 200

        project_list = response.context['active_projects']
        assert public in project_list
        assert private in project_list
