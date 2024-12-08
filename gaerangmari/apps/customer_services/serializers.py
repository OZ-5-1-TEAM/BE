from rest_framework import serializers
from .models import CustomerInquiry

class AddressSerializer(serializers.Serializer):
    district = serializers.CharField(max_length=50)
    neighborhood = serializers.CharField(max_length=50)

class CustomerInquirySerializer(serializers.ModelSerializer):
    address = AddressSerializer(write_only=True)

    class Meta:
        model = CustomerInquiry
        fields = ('id', 'title', 'email', 'address', 'content', 'status', 'created_at')
        read_only_fields = ('status', 'created_at')

    def create(self, validated_data):
        address_data = validated_data.pop('address')
        inquiry = CustomerInquiry.objects.create(
            district=address_data['district'],
            neighborhood=address_data['neighborhood'],
            **validated_data
        )
        return inquiry

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['inquiry_id'] = ret.pop('id')
        return ret