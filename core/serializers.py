from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as BaseUserSerailizer
from store.models import Customer

class UserCreateSerializer (BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'username', 'password', 'email', 'first_name','last_name']
    
    def save (self, **kwargs):
        user = super().save(**kwargs)
        # print(user.email)
        Customer.objects.create(user=user)
        return user
        
class UserSerializer(BaseUserSerailizer):
    class Meta(BaseUserSerailizer.Meta):
        fields = ['id', 'username', 'email', 'first_name','last_name']