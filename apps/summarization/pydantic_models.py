"""Pydantic models for summarization responses."""

from typing import List
from typing import Literal
from typing import Optional

from pydantic import BaseModel
from pydantic import Field


class SummaryItem(BaseModel):
    """Response model for summarization."""

    title: str = Field(description="Title of the summary")
    summary: str = Field(description="The summary of the text or document")
    key_points: list[str] = Field(
        default_factory=list,
        description="Important points or keywords extracted from the text or document",
    )


class ModuleItem(BaseModel):
    """Response model for module summarization."""

    module_name: str = Field(description="Name of the module")
    summary: str = Field(description="Summary of the module")
    key_points: list[str] = Field(
        default_factory=list, description="Key points of the module"
    )
    phase_status: str = Field(
        description="Phase status: 'past' (in the past), 'active' (currently running), 'upcoming' (in the future)"
    )
    link: str = Field(description="Link to the module")


class SummaryResponse(BaseModel):
    """Response model for summarization."""

    summary_items: list[SummaryItem] = Field(
        default_factory=list,
        description=(
            "List of summary items. Each item contains: "
            "title, summary, key_points (list of important points)"
        ),
    )
    module_items: list[ModuleItem] = Field(
        default_factory=list,
        description=(
            "List of module items. Each item contains: "
            "module_name, summary, key_points (list of important points), "
            "phase_status (past/active/upcoming), link (URL to the module)"
        ),
    )


"""Pydantic models for summarization responses."""


# Debug sub-models
class Claim(BaseModel):
    """A claim extracted from the summary with evidence."""

    claim_text: str = Field(description="The claim text")
    evidence_type: Literal[
        "from_votes",
        "from_ratings",
        "from_open_answers",
        "from_comments",
        "from_base_text",
        "uncertain",
    ] = Field(description="Type of evidence supporting this claim")
    action: Literal["keep", "soften", "replace", "remove"] = Field(
        description="Action taken on this claim"
    )
    fix_hint: Optional[str] = Field(None, description="Hint for fixing the claim")


class QuantifierFix(BaseModel):
    """A fix for an uncertain quantifier."""

    original_phrase: str = Field(description="Original uncertain phrase")
    replacement: str = Field(description="Replacement phrase")
    reason: str = Field(description="Reason for the fix")


class Patch(BaseModel):
    """A patch applied to the summary."""

    patch_type: Literal["REPLACE", "REMOVE", "ADD_SENTENCE"] = Field(
        description="Type of patch applied"
    )
    target: str = Field(description="Target text to patch")
    replacement: Optional[str] = Field(
        None, description="Replacement text (for REPLACE/ADD)"
    )


class ModuleDebug(BaseModel):
    """Debug information for a module summary."""

    module_type: str = Field(description="Type of module")
    signals_snapshot: List[str] = Field(
        default_factory=list, description="Snapshot of signals at generation time"
    )
    draft_before_qa: str = Field(description="Draft summary before QA")
    claims: List[Claim] = Field(
        default_factory=list, description="Claims extracted from summary"
    )
    quantifier_fixes: List[QuantifierFix] = Field(
        default_factory=list, description="Fixes for uncertain quantifiers"
    )
    anchors: List[str] = Field(
        default_factory=list, description="Anchor points in the data"
    )
    coverage_gaps: List[str] = Field(
        default_factory=list, description="Identified gaps in coverage"
    )
    coverage_patch: Optional[str] = Field(
        None, description="Patch to fix coverage gaps"
    )
    patches: List[Patch] = Field(default_factory=list, description="Patches applied")
    after_qa: str = Field(description="Summary after QA process")
    diff_summary: Optional[str] = Field(None, description="Summary of changes made")
    qa_status: Literal["PASS", "FAIL"] = Field(description="QA status")


class ModuleFinal(BaseModel):
    """Final summary and bullets for a module."""

    summary: str = Field(description="Summary of the module's outcomes/activities")
    bullets: List[str] = Field(
        default_factory=list,
        description="Key points or main sentiments from the module",
    )


class PhaseModule(BaseModel):
    """Module within a phase section."""

    module_name: str = Field(description="Name of the module")
    module_id: int = Field(description="ID of the module")
    status: Literal["past", "current", "upcoming"] = Field(description="Module status")
    debug: Optional[ModuleDebug] = Field(None, description="Debug information")
    final: ModuleFinal = Field(description="Summary and key points for the module")


class PhaseSection(BaseModel):
    """A phase section containing modules."""

    modules: List[PhaseModule] = Field(
        default_factory=list, description="Modules in this phase"
    )


class Phases(BaseModel):
    """All phase sections."""

    past: PhaseSection = Field(default_factory=PhaseSection)
    current: PhaseSection = Field(default_factory=PhaseSection)
    upcoming: PhaseSection = Field(default_factory=PhaseSection)


class GeneralInfo(BaseModel):
    """General information about the project."""

    summary: str = Field(description="General summary of the entire project")
    goals: List[str] = Field(
        default_factory=list, description="Overall goals of the project"
    )


class ProjectSummaryResponse(BaseModel):
    """Response model for complete project summarization."""

    title: str = Field(default="Summary of participation")
    general_info: GeneralInfo = Field(description="General project information")
    phases: Phases = Field(description="All phase sections with their modules")


class DocumentInputItem(BaseModel):
    """Single document input item with handle and URL."""

    handle: str = Field(description="Unique identifier/handle for the document")
    url: str = Field(description="URL of the document")

    def is_image(self) -> bool:
        """Check if the URL points to an image file."""
        image_extensions = (
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".webp",
            ".mpo",
            ".heif",
            ".avif",
            ".bmp",
            ".tiff",
            ".tif",
        )
        url_lower = self.url.lower()
        return any(url_lower.endswith(ext) for ext in image_extensions)

    def is_document(self) -> bool:
        """Check if the URL points to a document file (non-image)."""
        document_extensions = (".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt")
        url_lower = self.url.lower()
        return any(url_lower.endswith(ext) for ext in document_extensions)


class DocumentSummaryItem(BaseModel):
    """Response model for a single document summary with handle."""

    handle: str = Field(description="Unique identifier/handle for the document")
    summary: str = Field(description="Summary of the document content")


class DocumentSummaryResponse(BaseModel):
    """Response model for multiple document summaries."""

    documents: list[DocumentSummaryItem] = Field(
        default_factory=list,
        description="List of document summaries, each with handle and summary",
    )
