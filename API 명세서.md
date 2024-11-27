# API 명세서

## 1. 인증 (Authentication)

### 1.1 회원가입
- **Endpoint**: `POST /api/v1/auth/signup`
- **Description**: 새로운 사용자 계정을 생성합니다.

| Request Body | Type | Required | Description |
|-------------|------|----------|-------------|
| email | string | Yes | 사용자 이메일 |
| password | string | Yes | 사용자 비밀번호 |
| nickname | string | Yes | 사용자 닉네임 |

**Response**
```json
{
    "user_id": 1,
    "email": "user@example.com",
    "nickname": "username",
    "created_at": "2024-11-19T12:00:00Z"
}
```

### 1.2 로그인
- **Endpoint**: `POST /api/v1/auth/login`
- **Description**: 사용자 인증 및 토큰 발급

| Request Body | Type | Required | Description |
|-------------|------|----------|-------------|
| email | string | Yes | 사용자 이메일 |
| password | string | Yes | 사용자 비밀번호 |

**Response**
```json
{
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "nickname": "username"
    }
}
```

### 1.3 소셜 로그인
- **Endpoint**: `POST /api/v1/auth/social-login`
- **Description**: 소셜 미디어를 통한 로그인

| Request Body | Type | Required | Description |
|-------------|------|----------|-------------|
| provider | string | Yes | "kakao" 또는 "google" |
| token | string | Yes | 소셜 인증 토큰 |

## 2. 반려동물 관리 (Pet Management)

### 2.1 반려동물 등록
- **Endpoint**: `POST /api/v1/pets`
- **Description**: 새로운 반려동물 정보 등록

| Request Body | Type | Required | Description |
|-------------|------|----------|-------------|
| name | string | Yes | 반려동물 이름 |
| breed | string | Yes | 품종 |
| age | integer | No | 나이 |
| weight | float | No | 체중 |
| description | string | No | 설명 |
| image | file | No | 반려동물 사진 |

### 2.2 반려동물 조회
- **Endpoint**: `GET /api/v1/pets`
- **Description**: 등록된 반려동물 목록 조회

**Response**
```json
{
    "pets": [
        {
            "id": 1,
            "name": "멍멍이",
            "breed": "골든리트리버",
            "age": 3,
            "weight": 25.5,
            "image_url": "https://example.com/pet.jpg",
            "description": "활발한 성격의 강아지"
        }
    ]
}
```

## 3. 게시글 관리 (Post Management)

### 3.1 게시글 작성
- **Endpoint**: `POST /api/v1/posts`
- **Description**: 새로운 게시글 작성

| Request Body | Type | Required | Description |
|-------------|------|----------|-------------|
| category | string | Yes | 게시글 카테고리 |
| title | string | Yes | 제목 |
| content | string | Yes | 내용 |
| district | string | Yes | 구 |
| neighborhood | string | Yes | 동 |
| images | file[] | No | 이미지 파일 배열 |

### 3.2 게시글 검색
- **Endpoint**: `GET /api/v1/posts`
- **Description**: 게시글 검색 및 조회

| Query Parameter | Type | Required | Description |
|----------------|------|----------|-------------|
| category | string | No | 카테고리 필터 |
| district | string | No | 구 필터 |
| neighborhood | string | No | 동 필터 |
| keyword | string | No | 검색어 |
| sort | string | No | 정렬 방식 (latest/popular) |
| page | integer | No | 페이지 번호 |
| size | integer | No | 페이지 크기 |

## 4. 메시지 (Messages)

### 4.1 쪽지 보내기
- **Endpoint**: `POST /api/v1/messages`
- **Description**: 다른 사용자에게 쪽지 전송

| Request Body | Type | Required | Description |
|-------------|------|----------|-------------|
| receiver_id | integer | Yes | 수신자 ID |
| content | string | Yes | 쪽지 내용 |

### 4.2 쪽지함 조회
- **Endpoint**: `GET /api/v1/messages`
- **Description**: 받은/보낸 쪽지 목록 조회

| Query Parameter | Type | Required | Description |
|----------------|------|----------|-------------|
| type | string | Yes | received/sent |
| page | integer | No | 페이지 번호 |
| size | integer | No | 페이지 크기 |

## 5. 알림 (Notifications)

### 5.1 알림 목록 조회
- **Endpoint**: `GET /api/v1/notifications`
- **Description**: 사용자의 알림 목록 조회

### 5.2 알림 읽음 처리
- **Endpoint**: `PUT /api/v1/notifications/{notification_id}/read`
- **Description**: 특정 알림을 읽음 상태로 변경

## 6. 친구 관리 (Friends)

### 6.1 친구 요청
- **Endpoint**: `POST /api/v1/friends/request`
- **Description**: 다른 사용자에게 친구 요청 전송

| Request Body | Type | Required | Description |
|-------------|------|----------|-------------|
| addressee_id | integer | Yes | 수신자 ID |

### 6.2 친구 요청 응답
- **Endpoint**: `PUT /api/v1/friends/request/{request_id}`
- **Description**: 받은 친구 요청에 대한 수락/거절

| Request Body | Type | Required | Description |
|-------------|------|----------|-------------|
| status | string | Yes | "accepted" 또는 "rejected" |
