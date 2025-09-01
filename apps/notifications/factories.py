# notifications/factories.py
from typing import Optional
from adhocracy4.actions.models import Action
from .strategies import (
    NewsletterStrategy,
    ProjectUpdatesStrategy,
    ProjectEventsStrategy,
    UserEngagementStrategy
)
from .strategies.base import BaseNotificationStrategy

class NotificationStrategyFactory:
    """
    Factory class to retrieve the appropriate notification strategy
    for a given action.
    """
    def __init__(self):
        self.strategies = [
            NewsletterStrategy(),
            ProjectUpdatesStrategy(),
            ProjectEventsStrategy(),
            UserEngagementStrategy()
        ]
    
    def get_strategy(self, action: Action) -> Optional[BaseNotificationStrategy]:
        """
        Get the first strategy that can handle the given action.
        
        Args:
            action: The action to find a strategy for
            
        Returns:
            Appropriate strategy instance or None if no strategy found
        """
        for strategy in self.strategies:
            if strategy.can_handle(action):
                return strategy
        return None
    
    def get_all_strategies(self) -> list[BaseNotificationStrategy]:
        """Get all available strategy instances."""
        return self.strategies
    
    def get_strategy_for_type(self, strategy_type: str) -> Optional[BaseNotificationStrategy]:
        """
        Get strategy by type name.
        
        Args:
            strategy_type: One of 'newsletter', 'project_updates', etc.
            
        Returns:
            Strategy instance or None if not found
        """
        type_map = {
            'newsletter': NewsletterStrategy,
            'project_updates': ProjectUpdatesStrategy,
            'project_events': ProjectEventsStrategy,
            'user_engagement': UserEngagementStrategy
        }
        
        strategy_class = type_map.get(strategy_type)
        return strategy_class() if strategy_class else None