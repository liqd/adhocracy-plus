from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

from .serializers import AccountSerializer


class AccountViewSet(RetrieveUpdateAPIView):

    serializer_class = AccountSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ["get", "put"]

    def get_object(self):
        return self.request.user
