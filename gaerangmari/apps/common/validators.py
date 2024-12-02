import re

from django.core.exceptions import ValidationError


def validate_password(password):
    """비밀번호 유효성 검사"""
    if len(password) < 8:
        raise ValidationError("비밀번호는 8자 이상이어야 합니다.")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError("비밀번호는 특수문자를 포함해야 합니다.")


def validate_nickname(nickname):
    """닉네임 유효성 검사"""
    if len(nickname) < 2 or len(nickname) > 10:
        raise ValidationError("닉네임은 2~10자 사이여야 합니다.")
