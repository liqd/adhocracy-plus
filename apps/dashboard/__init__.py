from adhocracy4.dashboard import ProjectDashboard
from adhocracy4.dashboard import components

default_app_config = 'apps.dashboard.apps.Config'


class TypedProjectDashboard(ProjectDashboard):
    def get_project_components(self):
        return [component for component in components.get_project_components()
                if component.is_effective(self.project)]

    def get_module_components(self):
        return components.get_module_components()
