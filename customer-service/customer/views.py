from rest_framework.response import Response
from rest_framework import status
from .models import Customer
from .serializers import CustomerSerializer
from shared.base.views import BaseViewSet

class CustomerViewSet(BaseViewSet):
    """
    ViewSet for managing Customer model.
    Only returns and operates on the customer record linked to the logged-in Keycloak user.
    """

    serializer_class = CustomerSerializer

    def get_queryset(self):
        return Customer.objects.filter(keycloak_user_id=self.request.user.sub)

    def perform_create(self, serializer):
        serializer.save(
            keycloak_user_id=self.request.user.sub,
            username=self.request.user.username,
            email=self.request.user.email
        )
        
        
    def perform_update(self, serializer):
        serializer.save(keycloak_user_id=self.request.user.sub)

    def perform_destroy(self, instance):
        instance.delete()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        user = request.user.username
        print("username", user)
        print("the uuid",request.user.sub)
        if Customer.objects.filter(keycloak_user_id=request.user.sub).exists():
            return Response(
                {"detail": "Customer profile already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
