from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    객체의 소유자만 접근 가능
    """

    message = "해당 객체에 대한 권한이 없습니다."

    def has_object_permission(self, request, view, obj):
        return hasattr(obj, "user") and obj.user == request.user


class IsAdmin(permissions.BasePermission):
    """
    관리자만 접근 가능
    """

    message = "관리자만 접근할 수 있습니다."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff


class IsActiveUser(permissions.BasePermission):
    """
    활성 상태인 사용자만 접근 가능
    """

    message = "계정이 비활성화되었거나 정지된 상태입니다."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.status == "active"


class IsSocialUser(permissions.BasePermission):
    """
    소셜 로그인 사용자 접근 제한
    """

    message = "소셜 로그인 사용자는 이 기능을 사용할 수 없습니다."

    def has_permission(self, request, view):
        return request.user.is_authenticated and not request.user.is_social


class IsProfileOwner(permissions.BasePermission):
    """
    프로필 소유자만 접근 가능
    """

    message = "해당 프로필에 대한 권한이 없습니다."

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "user"):
            return obj.user == request.user
        return obj == request.user


class IsMessageParticipant(permissions.BasePermission):
    """쪽지 참여자(발신자/수신자) 권한"""

    message = "이 쪽지에 대한 접근 권한이 없습니다."

    def has_object_permission(self, request, view, obj):
        user = request.user
        # 삭제된 메시지에 대한 접근 제한
        if obj.is_deleted:
            return False
        # 발신자가 삭제한 메시지는 발신자가 접근 불가
        if user == obj.sender and obj.deleted_by_sender:
            return False
        # 수신자가 삭제한 메시지는 수신자가 접근 불가
        if user == obj.receiver and obj.deleted_by_receiver:
            return False
        # 발신자나 수신자만 접근 가능
        return obj.sender == user or obj.receiver == user


class IsRequestReceiver(permissions.BasePermission):
    """친구 요청 수신자 권한"""

    message = "이 요청에 대한 응답 권한이 없습니다."

    def has_object_permission(self, request, view, obj):
        return obj.to_user == request.user and obj.status == "pending"


# 이후에 views.py에 각 permission_classes 추가 등 작업
