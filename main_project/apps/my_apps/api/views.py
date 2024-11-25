from rest_framework import mixins, generics
from .serializers import MyModelSerializer

class MyModelView(generics.GenericAPIView):
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer
