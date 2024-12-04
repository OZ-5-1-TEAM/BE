# API 명세서

## 1. 인증 (Authentication)

### 1.1 회원가입
- **Endpoint**: `POST /api/v1/auth/signup`
- **Description**: 새로운 사용자 계정을 생성
- **Request Body**:

```json
{
    "email": "string",       // 이메일 (필수)
    "password": "string",    // 비밀번호 (필수, 8자 이상, 특수문자 포함)
    "nickname": "string"     // 닉네임 (필수, 2~10자)
}
```

- **Response (201 Created)**:
```json
{
    "user_id": 1,
    "email": "user@example.com",
    "nickname": "username",
    "created_at": "2024-11-19T12:00:00Z"
}
```

- **Error Responses**:
  - 400 Bad Request: 잘못된 입력 값
    ```json
    {
        "error": "INVALID_INPUT",
        "message": "이메일 형식이 올바르지 않습니다",
        "details": {
            "email": ["올바른 이메일 주소를 입력하세요."]
        }
    }
    ```
  - 409 Conflict: 중복된 이메일/닉네임
    ```json
    {
        "error": "DUPLICATE_VALUE",
        "message": "이미 사용 중인 이메일입니다"
    }
    ```

### 1.2 로그인
- **Endpoint**: `POST /api/v1/auth/login`
- **Description**: 사용자 인증 및 토큰 발급
- **Request Body**:

```json
{
    "email": "string",
    "password": "string"
}
```

- **Response (200 OK)**:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "nickname": "username"
    }
}
```

- **Error Responses**:
  - 401 Unauthorized: 인증 실패
    ```json
    {
        "error": "AUTHENTICATION_FAILED",
        "message": "이메일 또는 비밀번호가 올바르지 않습니다"
    }
    ```

### 1.3 소셜 로그인
- **Endpoint**: `POST /api/v1/auth/social-login`
- **Description**: 소셜 미디어를 통한 로그인
- **Request Body**:

```json
{
    "provider": "string",    // "kakao" 또는 "google"
    "access_token": "string" // 소셜 플랫폼에서 받은 액세스 토큰
}
```

- **Response (200 OK)**: 일반 로그인과 동일
- **Error Responses**:
  - 401 Unauthorized: 유효하지 않은 소셜 토큰
  - 400 Bad Request: 지원하지 않는 provider

### 1.4 비밀번호 재설정
- **Endpoint**: `POST /api/v1/auth/reset-password`
- **Description**: 임시 비밀번호 발급
- **Request Body**:

```json
{
    "email": "string"
}
```

- **Response (200 OK)**:
```json
{
    "message": "임시 비밀번호가 이메일로 전송되었습니다"
}
```

## 2. 사용자 관리 (User Management)

### 2.1 사용자 정보 조회
- **Endpoint**: `GET /api/v1/users/me`
- **Description**: 현재 로그인한 사용자 정보 조회
- **Headers**: Authorization: Bearer {access_token}
- **Response (200 OK)**:

```json
{
    "id": 1,
    "email": "user@example.com",
    "nickname": "username",
    "created_at": "2024-11-19T12:00:00Z",
    "profile_image": "https://example.com/images/profile.jpg",
    "location": {
        "district": "강남구",
        "neighborhood": "역삼동"
    }
}
```

### 2.2 사용자 정보 수정
- **Endpoint**: `PUT /api/v1/users/me`
- **Description**: 사용자 정보 수정
- **Headers**: Authorization: Bearer {access_token}
- **Request Body**:

```json
{
    "nickname": "string",
    "password": "string",        // 선택적
    "profile_image": "file",     // 선택적
    "location": {                // 선택적
        "district": "string",
        "neighborhood": "string"
    }
}
```

- **Response (200 OK)**:
```json
{
    "message": "사용자 정보가 수정되었습니다",
    "user": {
        "id": 1,
        "nickname": "new_username",
        "profile_image": "https://example.com/images/new_profile.jpg",
        "location": {
            "district": "강남구",
            "neighborhood": "역삼동"
        }
    }
}
```

### 2.3 회원 탈퇴
- **Endpoint**: `DELETE /api/v1/users/me`
- **Description**: 회원 탈퇴 처리
- **Headers**: Authorization: Bearer {access_token}
- **Response (204 No Content)**

## 3. 관리자 권한 (Admin)

### 3.1 사용자 목록 조회 (관리자용)
- **Endpoint**: `GET /api/v1/admin/users`
- **Description**: 전체 사용자 목록 조회
- **Headers**: Authorization: Bearer {access_token}
- **Permission**: Admin only
- **Query Parameters**:
  - page: 페이지 번호 (기본값: 1)
  - size: 페이지 크기 (기본값: 20)
  - search: 검색어 (이메일, 닉네임)
  - status: 계정 상태 (active/inactive/suspended)

- **Response (200 OK)**:
```json
{
    "total": 100,
    "page": 1,
    "size": 20,
    "users": [
        {
            "id": 1,
            "email": "user@example.com",
            "nickname": "username",
            "status": "active",
            "created_at": "2024-11-19T12:00:00Z",
            "last_login": "2024-12-02T15:00:00Z"
        }
    ]
}
```

### 3.2 사용자 상태 변경 (관리자용)
- **Endpoint**: `PUT /api/v1/admin/users/{user_id}/status`
- **Description**: 사용자 계정 상태 변경
- **Headers**: Authorization: Bearer {access_token}
- **Permission**: Admin only
- **Request Body**:

```json
{
    "status": "string",     // active/inactive/suspended
    "reason": "string"      // 상태 변경 사유
}
```

- **Response (200 OK)**:
```json
{
    "message": "사용자 상태가 변경되었습니다",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "status": "suspended",
        "status_changed_at": "2024-12-02T15:00:00Z",
        "status_reason": "이용약관 위반"
    }
}
```

# API 명세서

## 1. 반려동물 관리 (Pet Management)

### 1.1 반려동물 등록
- **Endpoint**: `POST /api/v1/pets`
- **Description**: 새로운 반려동물 정보 등록
- **Headers**: Authorization: Bearer {access_token}
- **Request Body**: multipart/form-data

```json
{
    "name": "string",          // 필수
    "breed": "string",         // 필수
    "age": "integer",         // 선택
    "weight": "float",        // 선택
    "size": "string",         // 필수 (small/medium/large)
    "description": "string",   // 선택
    "image": "file"           // 선택, 이미지 파일
}
```

- **Response (201 Created)**:
```json
{
    "id": 1,
    "name": "멍멍이",
    "breed": "골든리트리버",
    "age": 3,
    "weight": 25.5,
    "size": "large",
    "description": "활발한 성격의 강아지",
    "image_url": "https://petservice-s3.amazonaws.com/pets/image1.jpg",
    "created_at": "2024-12-02T15:00:00Z"
}
```

### 1.2 반려동물 목록 조회
- **Endpoint**: `GET /api/v1/pets`
- **Description**: 사용자의 반려동물 목록 조회
- **Headers**: Authorization: Bearer {access_token}
- **Response (200 OK)**:

```json
{
    "pets": [
        {
            "id": 1,
            "name": "멍멍이",
            "breed": "골든리트리버",
            "age": 3,
            "weight": 25.5,
            "size": "large",
            "image_url": "https://petservice-s3.amazonaws.com/pets/image1.jpg",
            "created_at": "2024-12-02T15:00:00Z"
        }
    ]
}
```

### 1.3 반려동물 정보 수정
- **Endpoint**: `PUT /api/v1/pets/{pet_id}`
- **Headers**: Authorization: Bearer {access_token}
- **Request Body**: multipart/form-data (1.1과 동일)
- **Response (200 OK)**: 수정된 반려동물 정보

### 1.4 반려동물 삭제
- **Endpoint**: `DELETE /api/v1/pets/{pet_id}`
- **Headers**: Authorization: Bearer {access_token}
- **Response (204 No Content)**

## 2. 게시글 관리 (Post Management)

### 2.1 게시글 작성
- **Endpoint**: `POST /api/v1/posts`
- **Description**: 새로운 게시글 작성
- **Headers**: Authorization: Bearer {access_token}
- **Request Body**: multipart/form-data

```json
{
    "title": "string",         // 필수
    "content": "string",       // 필수
    "category": "string",      // 필수 (notice/walk/care/community)
    "district": "string",      // 필수 (구)
    "neighborhood": "string",  // 필수 (동)
    "dog_size": "string",     // 선택 (small/medium/large)
    "images": ["file"]        // 선택, 최대 5개 이미지
}
```

- **Response (201 Created)**:
```json
{
    "id": 1,
    "title": "산책 친구 구해요",
    "content": "주말 아침에 같이 산책하실 분 구합니다",
    "category": "walk",
    "location": {
        "district": "강남구",
        "neighborhood": "역삼동"
    },
    "dog_size": "medium",
    "author": {
        "id": 1,
        "nickname": "사용자",
        "profile_image": "https://example.com/profile.jpg"
    },
    "images": [
        "https://petservice-s3.amazonaws.com/posts/image1.jpg"
    ],
    "likes_count": 0,
    "comments_count": 0,
    "created_at": "2024-12-02T15:00:00Z"
}
```

### 2.2 게시글 목록 조회
- **Endpoint**: `GET /api/v1/posts`
- **Query Parameters**:
  - category: 게시글 카테고리
  - district: 구 필터
  - neighborhood: 동 필터
  - dog_size: 강아지 크기
  - keyword: 검색어 (제목, 내용)
  - sort: 정렬 방식 (latest/popular)
  - page: 페이지 번호
  - size: 페이지 크기

- **Response (200 OK)**:
```json
{
    "total": 100,
    "page": 1,
    "size": 20,
    "posts": [
        {
            "id": 1,
            "title": "산책 친구 구해요",
            "category": "walk",
            "location": {
                "district": "강남구",
                "neighborhood": "역삼동"
            },
            "author": {
                "id": 1,
                "nickname": "사용자"
            },
            "thumbnail": "https://petservice-s3.amazonaws.com/posts/thumb1.jpg",
            "likes_count": 5,
            "comments_count": 3,
            "created_at": "2024-12-02T15:00:00Z"
        }
    ]
}
```

### 2.3 게시글 상세 조회
- **Endpoint**: `GET /api/v1/posts/{post_id}`
- **Response (200 OK)**:
```json
{
    "id": 1,
    "title": "산책 친구 구해요",
    "content": "주말 아침에 같이 산책하실 분 구합니다",
    "category": "walk",
    "location": {
        "district": "강남구",
        "neighborhood": "역삼동"
    },
    "dog_size": "medium",
    "author": {
        "id": 1,
        "nickname": "사용자",
        "profile_image": "https://example.com/profile.jpg"
    },
    "images": [
        "https://petservice-s3.amazonaws.com/posts/image1.jpg"
    ],
    "likes_count": 5,
    "comments_count": 3,
    "is_liked": true,
    "created_at": "2024-12-02T15:00:00Z",
    "comments": [
        {
            "id": 1,
            "content": "저도 참여하고 싶어요",
            "author": {
                "id": 2,
                "nickname": "댓글작성자"
            },
            "created_at": "2024-12-02T15:30:00Z",
            "replies": [
                {
                    "id": 2,
                    "content": "네, 연락주세요",
                    "author": {
                        "id": 1,
                        "nickname": "사용자"
                    },
                    "created_at": "2024-12-02T15:35:00Z"
                }
            ]
        }
    ]
}
```

### 2.4 게시글 수정
- **Endpoint**: `PUT /api/v1/posts/{post_id}`
- **Headers**: Authorization: Bearer {access_token}
- **Request Body**: 2.1과 동일
- **Response (200 OK)**: 수정된 게시글 정보

### 2.5 게시글 삭제
- **Endpoint**: `DELETE /api/v1/posts/{post_id}`
- **Headers**: Authorization: Bearer {access_token}
- **Response (204 No Content)**

### 2.6 게시글 좋아요/취소
- **Endpoint**: `POST /api/v1/posts/{post_id}/like`
- **Headers**: Authorization: Bearer {access_token}
- **Response (200 OK)**:
```json
{
    "is_liked": true,
    "likes_count": 6
}
```

# API 명세서

## 1. 쪽지 관리 (Messages)

### 1.1 쪽지 보내기
- **Endpoint**: `POST /api/v1/messages`
- **Description**: 다른 사용자에게 쪽지 전송
- **Headers**: Authorization: Bearer {access_token}
- **Request Body**:
```json
{
    "receiver_id": "integer", // 자기 자신에게 전송 불가
    "content": "string" // 최대 500자
}
```

- **Response (201 Created)**:
```json
{
    "id": 1,
    "sender": {
        "id": 1,
        "nickname": "발신자"
    },
    "receiver": {
        "id": 2,
        "nickname": "수신자"
    },
    "content": "안녕하세요, 산책 같이 하실래요?",
    "created_at": "2024-12-02T15:00:00Z",
    "is_read": false
}
```

### 1.2 받은 쪽지함 조회
- **Endpoint**: `GET /api/v1/messages/received`
- **Headers**: Authorization: Bearer {access_token}
- **Query Parameters**:
  - page: 페이지 번호 (기본값: 1)
  - size: 페이지 크기 (기본값: 20)

- **Response (200 OK)**:
```json
{
    "total": 50,
    "page": 1,
    "size": 20,
    "messages": [
        {
            "id": 1,
            "sender": {
                "id": 2,
                "nickname": "발신자",
                "profile_image": "https://example.com/profile.jpg"
            },
            "content": "안녕하세요, 산책 같이 하실래요?",
            "created_at": "2024-12-02T15:00:00Z",
            "is_read": false
        }
    ]
}
```

### 1.3 보낸 쪽지함 조회
- **Endpoint**: `GET /api/v1/messages/sent`
- **Headers**: Authorization: Bearer {access_token}
- **Query Parameters**: 받은 쪽지함과 동일
- **Response**: 받은 쪽지함과 동일한 형식

### 1.4 쪽지 읽음 처리
- **Endpoint**: `PUT /api/v1/messages/{message_id}/read`
- **Headers**: Authorization: Bearer {access_token}
- **Response (200 OK)**:
```json
{
    "message_id": 1,
    "is_read": true,
    "read_at": "2024-12-02T15:30:00Z"
}
```

### 1.5 쪽지 삭제
- **Endpoint**: `DELETE /api/v1/messages/{message_id}`
- **Headers**: Authorization: Bearer {access_token}
- **Response (204 No Content)**

## 2. 친구 관리 (Friends)

### 2.1 친구 요청 보내기
- **Endpoint**: `POST /api/v1/friends/requests`
- **Headers**: Authorization: Bearer {access_token}
- **Request Body**:
```json
{
    "receiver_id": "integer"  // 수신자 ID (필수)
}
```

- **Response (201 Created)**:
```json
{
    "request_id": 1,
    "sender": {
        "id": 1,
        "nickname": "요청자"
    },
    "receiver": {
        "id": 2,
        "nickname": "수신자"
    },
    "status": "pending",
    "created_at": "2024-12-02T15:00:00Z"
}
```

### 2.2 친구 요청 응답
- **Endpoint**: `PUT /api/v1/friends/requests/{request_id}`
- **Headers**: Authorization: Bearer {access_token}
- **Request Body**:
```json
{
    "status": "string"  // "accepted" 또는 "rejected"
}
```

- **Response (200 OK)**:
```json
{
    "request_id": 1,
    "status": "accepted",
    "updated_at": "2024-12-02T15:30:00Z"
}
```

### 2.3 친구 목록 조회
- **Endpoint**: `GET /api/v1/friends`
- **Headers**: Authorization: Bearer {access_token}
- **Query Parameters**:
  - page: 페이지 번호
  - size: 페이지 크기
  - search: 검색어 (닉네임)

- **Response (200 OK)**:
```json
{
    "total": 30,
    "page": 1,
    "size": 20,
    "friends": [
        {
            "id": 2,
            "nickname": "친구1",
            "profile_image": "https://example.com/profile.jpg",
            "friendship_date": "2024-11-19T12:00:00Z"
        }
    ]
}
```

### 2.4 친구 삭제
- **Endpoint**: `DELETE /api/v1/friends/{friend_id}`
- **Headers**: Authorization: Bearer {access_token}
- **Response (204 No Content)**

## 3. 알림 관리 (Notifications)

### 3.1 알림 목록 조회
- **Endpoint**: `GET /api/v1/notifications`
- **Headers**: Authorization: Bearer {access_token}
- **Query Parameters**:
  - page: 페이지 번호
  - size: 페이지 크기
  - is_read: 읽음 여부 필터 (true/false)

- **Response (200 OK)**:
```json
{
    "total": 50,
    "page": 1,
    "size": 20,
    "notifications": [
        {
            "id": 1,
            "type": "string",    // message/friend_request/comment/like
            "content": "새로운 쪽지가 도착했습니다",
            "sender": {          // 알림 발신자 정보 (있는 경우)
                "id": 2,
                "nickname": "발신자"
            },
            "reference_id": 1,   // 참조 ID (쪽지 ID, 게시글 ID 등)
            "created_at": "2024-12-02T15:00:00Z",
            "is_read": false
        }
    ]
}
```

### 3.2 알림 읽음 처리
- **Endpoint**: `PUT /api/v1/notifications/{notification_id}/read`
- **Headers**: Authorization: Bearer {access_token}
- **Response (200 OK)**:
```json
{
    "notification_id": 1,
    "is_read": true,
    "read_at": "2024-12-02T15:30:00Z"
}
```

### 3.3 알림 전체 읽음 처리
- **Endpoint**: `PUT /api/v1/notifications/read-all`
- **Headers**: Authorization: Bearer {access_token}
- **Response (200 OK)**:
```json
{
    "updated_count": 10,
    "read_at": "2024-12-02T15:30:00Z"
}
```

### 3.4 알림 삭제
- **Endpoint**: `DELETE /api/v1/notifications/{notification_id}`
- **Headers**: Authorization: Bearer {access_token}
- **Response (204 No Content)**

### 3.5 푸시 알림 설정 관리
- **Endpoint**: `PUT /api/v1/notifications/settings`
- **Headers**: Authorization: Bearer {access_token}
- **Request Body**:
```json
{
    "push_enabled": true,           // 전체 푸시 알림 활성화 여부
    "message_notification": true,    // 쪽지 알림
    "friend_notification": true,     // 친구 관련 알림
    "comment_notification": true,    // 댓글 알림
    "like_notification": true       // 좋아요 알림
}
```

- **Response (200 OK)**:
```json
{
    "settings": {
        "push_enabled": true,
        "message_notification": true,
        "friend_notification": true,
        "comment_notification": true,
        "like_notification": true,
        "updated_at": "2024-12-02T15:30:00Z"
    }
}
```

# API 명세서

## 1. 공지사항 관리 (Notices)

### 1.1 공지사항 작성
- **Endpoint**: `POST /api/v1/notices`
- **Description**: 공지사항 작성 (관리자 전용)
- **Headers**: Authorization: Bearer {access_token}
- **Permission**: Admin only
- **Request Body**:
```json
{
    "title": "string",       // 필수
    "content": "string",     // 필수
    "is_pinned": "boolean", // 상단 고정 여부 (선택, 기본값: false)
    "images": ["file"]      // 선택, 최대 5개 이미지
}
```

- **Response (201 Created)**:
```json
{
    "id": 1,
    "title": "서비스 점검 안내",
    "content": "12월 5일 새벽 2시부터 4시까지 서버 점검이 있을 예정입니다.",
    "is_pinned": true,
    "author": {
        "id": 1,
        "nickname": "관리자"
    },
    "images": [
        "https://petservice-s3.amazonaws.com/notices/image1.jpg"
    ],
    "created_at": "2024-12-02T15:00:00Z"
}
```

### 1.2 공지사항 목록 조회
- **Endpoint**: `GET /api/v1/notices`
- **Query Parameters**:
  - page: 페이지 번호
  - size: 페이지 크기
  - search: 검색어 (제목, 내용)

- **Response (200 OK)**:
```json
{
    "total": 50,
    "page": 1,
    "size": 20,
    "notices": [
        {
            "id": 1,
            "title": "서비스 점검 안내",
            "is_pinned": true,
            "author": {
                "id": 1,
                "nickname": "관리자"
            },
            "created_at": "2024-12-02T15:00:00Z",
            "views": 1250
        }
    ]
}
```

### 1.3 공지사항 상세 조회
- **Endpoint**: `GET /api/v1/notices/{notice_id}`
- **Response (200 OK)**:
```json
{
    "id": 1,
    "title": "서비스 점검 안내",
    "content": "12월 5일 새벽 2시부터 4시까지 서버 점검이 있을 예정입니다.",
    "is_pinned": true,
    "author": {
        "id": 1,
        "nickname": "관리자"
    },
    "images": [
        "https://petservice-s3.amazonaws.com/notices/image1.jpg"
    ],
    "created_at": "2024-12-02T15:00:00Z",
    "updated_at": "2024-12-02T15:30:00Z",
    "views": 1250
}
```

### 1.4 공지사항 수정
- **Endpoint**: `PUT /api/v1/notices/{notice_id}`
- **Headers**: Authorization: Bearer {access_token}
- **Permission**: Admin only
- **Request Body**: 1.1과 동일
- **Response (200 OK)**: 수정된 공지사항 정보

### 1.5 공지사항 삭제
- **Endpoint**: `DELETE /api/v1/notices/{notice_id}`
- **Headers**: Authorization: Bearer {access_token}
- **Permission**: Admin only
- **Response (204 No Content)**

## 2. 관리자 추가 기능 (Admin Features)

### 2.1 신고 관리
#### 2.1.1 신고 목록 조회
- **Endpoint**: `GET /api/v1/admin/reports`
- **Headers**: Authorization: Bearer {access_token}
- **Permission**: Admin only
- **Query Parameters**:
  - page: 페이지 번호
  - size: 페이지 크기
  - status: 처리 상태 (pending/processed)
  - type: 신고 유형 (post/comment/user)

- **Response (200 OK)**:
```json
{
    "total": 100,
    "page": 1,
    "size": 20,
    "reports": [
        {
            "id": 1,
            "type": "post",
            "target_id": 123,
            "reporter": {
                "id": 2,
                "nickname": "신고자"
            },
            "reason": "부적절한 컨텐츠",
            "description": "광고성 게시글입니다",
            "status": "pending",
            "created_at": "2024-12-02T15:00:00Z"
        }
    ]
}
```

#### 2.1.2 신고 처리
- **Endpoint**: `PUT /api/v1/admin/reports/{report_id}`
- **Headers**: Authorization: Bearer {access_token}
- **Permission**: Admin only
- **Request Body**:
```json
{
    "status": "string",    // "accepted" 또는 "rejected"
    "action": "string",    // "delete" 또는 "warning" 또는 "block"
    "comment": "string"    // 처리 사유
}
```
