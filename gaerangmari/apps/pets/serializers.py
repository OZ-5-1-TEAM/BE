from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import Pet

class PetSerializer(serializers.ModelSerializer):
   """
   반려동물 시리얼라이저
   기본적인 CRUD 작업에 사용
   """
   owner_nickname = serializers.CharField(source="owner.nickname", read_only=True)
   photo = serializers.ImageField(source='image', required=False)
   photo_url = serializers.SerializerMethodField()
   additional_photo = serializers.ImageField(source='additional_image', required=False)
   additional_photo_url = serializers.SerializerMethodField()

   class Meta:
       model = Pet
       fields = (
           "id",
           "name", 
           "owner",
           "owner_nickname",
           "breed",
           "age",
           "weight",
           "size",
           "description",
           "gender",
           "photo",
           "photo_url",
           "additional_photo",
           "additional_photo_url",
           "created_at",
           "updated_at",
       )
       read_only_fields = ("owner", "created_at", "updated_at")
       extra_kwargs = {
           "photo": {"write_only": True},
           "additional_photo": {"write_only": True}
       }

   def get_photo_url(self, obj):
       if obj.image:
           return obj.image.url
       return None

   def get_additional_photo_url(self, obj):
       if obj.additional_image:
           return obj.additional_image.url
       return None

   def validate_weight(self, value):
       if value and value <= 0:
           raise serializers.ValidationError(_("무게는 0보다 커야 합니다."))
       return value

   def validate_age(self, value):
       if value and value < 0:
           raise serializers.ValidationError(_("나이는 0보다 작을 수 없습니다."))
       return value

   def create(self, validated_data):
       validated_data["owner"] = self.context["request"].user
       return super().create(validated_data)

class PetListSerializer(serializers.ModelSerializer):
   """
   반려동물 목록 조회용 시리얼라이저
   """
   owner_nickname = serializers.CharField(source="owner.nickname", read_only=True)
   photo_url = serializers.SerializerMethodField()

   class Meta:
       model = Pet
       fields = (
           "id",
           "name",
           "owner_nickname",
           "breed",
           "size",
           "gender",
           "photo_url",
           "created_at",
       )

   def get_photo_url(self, obj):
       if obj.image:
           return obj.image.url
       return None

class PetDetailSerializer(PetSerializer):
   """
   반려동물 상세 정보 시리얼라이저
   기본 시리얼라이저를 상속받아 추가 정보 포함
   """
   owner_profile = serializers.SerializerMethodField()

   class Meta(PetSerializer.Meta):
       fields = PetSerializer.Meta.fields + ("owner_profile",)

   def get_owner_profile(self, obj):
       return {
           "id": obj.owner.id,
           "nickname": obj.owner.nickname,
           "profile_image": obj.owner.profile_image.url if obj.owner.profile_image else None,
           "district": obj.owner.district,
           "neighborhood": obj.owner.neighborhood,
       }

class PetCreateSerializer(PetSerializer):
   """
   반려동물 생성 전용 시리얼라이저
   """
   photo = serializers.ImageField(source='image', required=False)
   additional_photo = serializers.ImageField(source='additional_image', required=False)
   
   class Meta(PetSerializer.Meta):
       fields = (
           "name", 
           "breed", 
           "age", 
           "weight", 
           "size", 
           "description", 
           "gender", 
           "photo", 
           "additional_photo"
       )

   def validate(self, data):
       user = self.context["request"].user
       if Pet.objects.filter(owner=user, is_deleted=False).count() >= 5:
           raise serializers.ValidationError(_("반려동물은 최대 5마리까지만 등록할 수 있습니다."))
       return data

class PetUpdateSerializer(PetSerializer):
   """
   반려동물 정보 수정 전용 시리얼라이저
   """
   photo = serializers.ImageField(source='image', required=False)
   additional_photo = serializers.ImageField(source='additional_image', required=False)
   
   class Meta(PetSerializer.Meta):
       fields = (
           "name", 
           "breed", 
           "age", 
           "weight", 
           "size", 
           "description", 
           "gender", 
           "photo", 
           "additional_photo"
       )
       extra_kwargs = {
           "name": {"required": False},
           "breed": {"required": False},
           "size": {"required": False},
           "gender": {"required": False},
       }

   def validate(self, data):
       if not data:
           raise serializers.ValidationError(_("수정할 정보를 입력해주세요."))
       return data

class PetImageUploadSerializer(serializers.ModelSerializer):
   """
   반려동물 이미지 업로드 전용 시리얼라이저
   """
   photo = serializers.ImageField(source='image', required=True)

   class Meta:
       model = Pet
       fields = ('photo',)