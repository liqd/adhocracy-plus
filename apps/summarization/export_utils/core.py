from adhocracy4.polls.models import Poll
from apps.budgeting.models import Proposal
from apps.debate.models import Subject
from apps.documents.models import Chapter
from apps.ideas.models import Idea
from apps.mapideas.models import MapIdea
from apps.offlineevents.models import OfflineEvent
from apps.topicprio.models import Topic

from .models.debates import export_debate
from .models.documents import export_document_chapters
from .models.ideas import export_idea
from .models.mapideas import export_mapidea
from .models.offline_events import export_offline_event
from .models.polls import export_poll
from .models.proposals import export_proposal
from .models.topics import export_topic
from .processing.cleaning import clean_export
from .processing.extractors import extract_attachments
from .processing.grouping import restructure_by_phase
from .processing.module_utils import get_module_status
from .processing.module_utils import get_module_type_from_name


def generate_full_export(project):
    """Generate complete project export data - module first approach"""
    from adhocracy4.modules.models import Module

    # Project metadata
    project_data = {
        "name": project.name,
        "description": project.description,
        "description_attachments": extract_attachments(project.description),
        "information": getattr(project, "information", None),
        "information_attachments": extract_attachments(
            getattr(project, "information", "")
        ),
        "slug": project.slug,
        "organisation": project.organisation.name,
        "result": project.result,
        "result_attachments": extract_attachments(project.result),
        "url": project.get_absolute_url(),
    }

    modules_data = []
    for module in Module.objects.filter(project=project, is_draft=False):
        module_data = {
            "module_id": module.id,
            "module_name": module.name,
            "module_type": get_module_type_from_name(module.name),
            "active_status": get_module_status(module),
            "module_start": str(module.module_start),
            "module_end": str(module.module_end),
            "description": module.description,
            "url": module.get_absolute_url(),
            "content": {},
        }

        # Ideas
        ideas = Idea.objects.filter(module=module)
        if ideas.exists():
            module_data["content"]["ideas"] = [export_idea(i) for i in ideas]

        # MapIdeas
        mapideas = (
            MapIdea.objects.filter(module__project=project)
            .select_related("category")
            .prefetch_related("labels")
        )
        if mapideas.exists():
            module_data["content"]["mapideas"] = [export_mapidea(m) for m in mapideas]

        # Polls
        polls = Poll.objects.filter(module=module).prefetch_related(
            "questions__choices__votes__other_vote",
        )
        if polls.exists():
            module_data["content"]["polls"] = [export_poll(p) for p in polls]

        # Topics
        topics = (
            Topic.objects.filter(module=module)
            .select_related("category")
            .prefetch_related("labels")
        )
        if topics.exists():
            module_data["content"]["topics"] = [export_topic(t) for t in topics]

        # Proposals
        proposals = (
            Proposal.objects.filter(module=module)
            .select_related("category")
            .prefetch_related("labels")
        )
        if proposals.exists():
            module_data["content"]["proposals"] = [
                export_proposal(p) for p in proposals
            ]

        # Debates
        debates = Subject.objects.filter(module=module)
        if debates.exists():
            module_data["content"]["debates"] = [export_debate(d) for d in debates]

        # Documents
        if Chapter.objects.filter(module=module).exists():
            module_data["content"]["documents"] = export_document_chapters(module)

        modules_data.append(module_data)

    # Offline events
    offline_events = []
    for event in OfflineEvent.objects.filter(project=project):
        offline_events.append(export_offline_event(event))

    export_data = {
        "project": project_data,
        "modules": modules_data,
        "offline_events": offline_events,
    }

    structured_result = restructure_by_phase(export_data)
    cleaned_result = clean_export(structured_result)
    return cleaned_result
