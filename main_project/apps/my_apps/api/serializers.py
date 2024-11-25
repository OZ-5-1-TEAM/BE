from rest_framework.serializers import ModelSerializer


class MyModelSerializer(ModelSerializer):
    class Meta:
        model = MyModel
        fields = ['field1', 'field2']
