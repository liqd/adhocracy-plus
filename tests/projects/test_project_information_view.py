import pytest
from django.urls import reverse

from adhocracy4.test.helpers import assert_template_response


def project_information_url(project):
    return reverse(
        "project-information",
        kwargs={
            "slug": project.slug,
            "organisation_slug": project.organisation.slug,
        },
    )


def project_detail_url(project):
    return reverse(
        "project-detail",
        kwargs={
            "slug": project.slug,
            "organisation_slug": project.organisation.slug,
        },
    )


@pytest.mark.django_db
def test_project_information_view(client, project_factory, module_factory, phase_factory):
    project = project_factory(
        is_draft=False,
        information="<p>Project background information.</p>",
        contact_name="Liquid Democracy e.V.",
        contact_address_text="Am Sudhaus 2\n12053 Berlin",
        contact_phone="+49 30 123456",
    )
    module = module_factory(project=project)
    phase_factory(module=module)

    response = client.get(project_information_url(project))

    assert response.status_code == 200
    assert_template_response(response, "a4_candy_projects/project_information.html")
    content = response.content.decode()
    assert "Project background information." in content
    assert "Liquid Democracy e.V." in content
    assert "Am Sudhaus 2" in content
    assert "Telephone" in content
    assert "+49 30 123456" in content
    assert "platform-breadcrumbs" in content
    assert "Information" in content


@pytest.mark.django_db
def test_project_information_back_link(client, project_factory, module_factory, phase_factory):
    project = project_factory(
        is_draft=False,
        information="<p>Project background information.</p>",
    )
    module = module_factory(project=project)
    phase_factory(module=module)

    response = client.get(project_information_url(project))

    assert project_detail_url(project) in response.content.decode()


@pytest.mark.django_db
def test_project_information_edit_button_for_moderator(
    client, project_factory, module_factory, phase_factory, organisation
):
    project = project_factory(
        organisation=organisation,
        is_draft=False,
        information="<p>Project background information.</p>",
    )
    module = module_factory(project=project)
    phase_factory(module=module)

    url = project_information_url(project)
    edit_url = reverse(
        "a4dashboard:dashboard-information-edit",
        kwargs={
            "organisation_slug": project.organisation.slug,
            "project_slug": project.slug,
        },
    )

    response = client.get(url)
    assert edit_url not in response.content.decode()

    initiator = organisation.initiators.first()
    client.login(username=initiator.email, password="password")
    response = client.get(url)

    assert response.status_code == 200
    assert edit_url in response.content.decode()


@pytest.mark.django_db
def test_project_detail_more_information_link(
    client, project_factory, module_factory, phase_factory
):
    project = project_factory(
        is_draft=False,
        information="<p>Project background information.</p>",
    )
    module_factory(project=project)
    module_factory(project=project)
    for module in project.published_modules.all():
        if not module.phase_set.exists():
            phase_factory(module=module)

    response = client.get(project_detail_url(project))

    assert response.status_code == 200
    assert project_information_url(project) in response.content.decode()
