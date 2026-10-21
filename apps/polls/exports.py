from adhocracy4.polls import exports as a4_poll_exports
from apps.exports.mixins import CreatorDisplayNameExportMixin


class PollCommentExportView(
    CreatorDisplayNameExportMixin, a4_poll_exports.PollCommentExportView
):
    """Poll comment export that marks guest creators."""
