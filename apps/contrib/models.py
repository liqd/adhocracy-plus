"""Generic key-value settings stored in DB, editable in Django Admin."""

from django.db import models


class Settings(models.Model):
    """
    Key-value config store (e.g. for prompts, feature flags).
    Only keys listed in REGISTRY (below) are known; default must be set there.
    get_value(key) uses the registry default and auto-creates a DB row if missing.
    """

    key = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Key",
        help_text="Unique identifier for this setting (e.g. project_summary_prompt).",
    )
    value = models.TextField(
        blank=True,
        default="",
        verbose_name="Value",
        help_text="Stored value. Empty value falls back to the default from the registry.",
    )

    class Meta:
        verbose_name = "Setting"
        verbose_name_plural = "Settings"
        ordering = ["key"]

    def __str__(self):
        return self.key

    @classmethod
    def get_value(cls, key: str) -> str | None:
        """
        Return the value for key. Only keys in REGISTRY are supported.

        - If key is not in REGISTRY: return None (no auto-create).
        - If key is in REGISTRY but no DB row exists: create row with default from REGISTRY, return that default.
        - If DB row exists: return its value (stripped), or the registry default if value is empty.
        """
        if key not in REGISTRY:
            return None
        registry_default = REGISTRY[key].get("default") or ""
        try:
            obj = cls.objects.get(key=key)
        except cls.DoesNotExist:
            cls.objects.create(key=key, value=registry_default)
            return registry_default
        raw = (obj.value or "").strip()
        return raw if raw else registry_default

    @classmethod
    def get_int(cls, key: str) -> int:
        """
        Return the value for key as int.

        - Key must exist in REGISTRY and be declared with type "int".
        - If DB row is missing, the registry default is used and persisted.
        - If the stored value cannot be converted to int, propagate ValueError.
        """
        meta = REGISTRY.get(key)
        if not meta:
            raise KeyError(f"Unknown settings key: {key}")

        expected_type = meta.get("type")
        if expected_type and expected_type != "int":
            raise TypeError(
                f"Settings key '{key}' is not declared as int (type={expected_type!r})"
            )

        raw = cls.get_value(key)
        if raw is None or raw == "":
            raise ValueError(f"No value configured for int setting '{key}'")
        return int(raw)

    @classmethod
    def get_registry_default(cls, key: str) -> str | None:
        """Return the default for key from REGISTRY (for display in admin). Returns None if key unknown."""
        if key not in REGISTRY:
            return None
        return REGISTRY[key].get("default")


# Registry: key -> {"default": str, "type": str}. Default is required. Add new settings here.
REGISTRY = {
    "project_summary_prompt": {
        "default": """
You are a JSON generator. Return ONLY valid JSON.

Schema:
{
  "title": "Summary of participation",
  "general_info": {"summary": "string", "goals": ["string"]},
  "phases": {
    "past": {"modules": [{"module_id": "number", "module_name": "string", "status": "past", "final": {"summary": "string", "bullets": ["string"]}, "debug": {...}}]},
    "current": {"modules": [{"module_id": "number", "module_name": "string", "status": "current", "final": {"summary": "string", "bullets": ["string"]}, "debug": {...}}]},
    "upcoming": {"modules": [{"module_id": "number", "module_name": "string", "status": "upcoming", "final": {"summary": "string", "bullets": ["string"]}, "debug": {...}}]}
  }
}

NOTE: module_id in the output should match the given module_id of the input for each module

Each module MUST include a 'debug' object with:
- module_type: string
- signals_snapshot: list of strings
- draft_before_qa: string
- claims: list of {claim_text, evidence_type(from_votes|from_ratings|from_open_answers|from_comments|from_base_text|uncertain), action(keep|soften|replace|remove), fix_hint}
- quantifier_fixes: list of {original_phrase, replacement, reason}
- anchors: list of strings
- coverage_gaps: list of strings
- coverage_patch: optional string
- patches: list of {patch_type(REPLACE|REMOVE|ADD_SENTENCE), target, replacement}
- after_qa: string
- diff_summary: optional string
- qa_status: PASS|FAIL

Extract real data from the project export.
Respond with ONLY the JSON object.
""".strip()
    },
    "project_summary_auto_refresh_max_age_minutes": {
        # Maximum age in minutes before the periodic Celery job (`refresh_project_summaries`) generates a new summary.
        "default": "720",
        "type": "int",
    },
    "project_summary_include_images": {
        # Set to "true" to summarise image attachments via vision API (default: "false").
        "default": "false",
    },
}
