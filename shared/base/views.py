from rest_framework.viewsets import ModelViewSet
from .permission import IsAuthenticated, IsAdmin, IsUser


"""     Base ViewSet with:
    1. Standardized UUID lookup
    2. Automatic softdelete filtering
    3. Default Authentication   """
class BaseViewSet(ModelViewSet):
    
    # lookup_field = 'id'
    permission_classes = [IsAuthenticated]

    
    def get_queryset(self):
        # Exclude softdeleted items
        return super().get_queryset().filter(is_active=True)