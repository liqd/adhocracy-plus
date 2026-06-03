import pytest
from django.urls import reverse


def project_results_url(project):
    return reverse(
        "project-results",
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
def test_project_results_redirects_when_nothing_to_show(
    client, project_factory, module_factory, phase_factory, project_insight_factory
):
    project = project_factory(is_draft=False, result="")
    module_factory(project=project)
    phase_factory(module=project.modules.first())
    project_insight_factory(project=project, display=False)

    response = client.get(project_results_url(project))

    assert response.status_code == 302
    assert response.url == project_detail_url(project)


@pytest.mark.django_db
def test_project_results_without_display_shows_result_text(
    client, project_factory, module_factory, phase_factory, project_insight_factory
):
    project = project_factory(
        is_draft=False,
        result="<p>Participation outcomes and next steps.</p>",
    )
    module_factory(project=project)
    phase_factory(module=project.modules.first())
    project_insight_factory(project=project, display=False)

    response = client.get(project_results_url(project))

    assert response.status_code == 200
    content = response.content.decode()
    assert "Participation outcomes and next steps." in content
    assert "project-detail__insights-value" not in content
