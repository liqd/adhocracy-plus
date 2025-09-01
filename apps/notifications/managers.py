from django.db import models


class NotificationManager(models.Manager):

    def for_user(self, user):
        return self.filter(recipient=user)

    def unread_for_user(self, user):
        return self.for_user(user).filter(read=False)

    def unread_count_for_user(self, user):
        return self.unread_for_user(user).count()
