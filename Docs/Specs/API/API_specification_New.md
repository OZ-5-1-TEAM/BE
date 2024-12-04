
### 모든 API는 인증된 사용자만 접근 가능(401 Unauthorized)


## 1. Users API

### User Authentication APIs
#### User Signup
```yaml
POST /api/users/signup/
Description: 사용자 회원가입
Request Body:
  - email: string (required)
  - password: string (required)
  - password_confirm: string (required)
  - nickname: string (required)
Responses:
  201: 회원가입 성공
  400: 잘못된 요청
```

#### User Detail
```yaml
GET /api/users/me/
Description: 사용자 상세 정보 조회
Responses:
  200:
    content:
      - email: string
      - nickname: string
      - profile: object
        - bio: string
  401: 인증되지 않음
```

#### Update User Detail
```yaml
PUT /api/users/me/
Description: 사용자 정보 수정
Request Body:
  - nickname: string (optional)
  - district: string (optional)
  - neighborhood: string (optional)
Responses:
  200: 수정 성공
  401: 인증되지 않음
```

#### Password Change
```yaml
POST /api/users/password-change/
Description: 비밀번호 변경
Request Body:
  - current_password: string (required)
  - new_password: string (required)
  - new_password_confirm: string (required)
Responses:
  200: 비밀번호 변경 성공
  400: 잘못된 요청
```

#### Social Login
```yaml
POST /api/users/social-login/
Description: 소셜 로그인 처리
Request Body:
  - provider: string (required) - 'kakao' or 'google'
  - access_token: string (required)
Responses:
  200: 로그인 성공
  400: 잘못된 요청
```

#### Password Reset
```yaml
POST /api/users/password-reset/
Description: 비밀번호 재설정 요청
Request Body:
  - email: string (required)
Responses:
  200: 이메일 발송 성공
  400: 잘못된 요청
```

## 2. Pets API

### Pet APIs
#### Create Pet
```yaml
POST /api/pets/
Description: 새로운 반려동물 등록
Request Body:
  - name: string (required)
  - breed: string (required)
  - age: integer (optional)
  - weight: float (optional)
  - size: string (optional)
  - description: string (optional)
  - image: file (optional)
Responses:
  201: 반려동물 생성 성공
  400: 잘못된 요청
```

#### Get Pet List
```yaml
GET /api/pets/
Description: 사용자의 반려동물 목록 조회
Responses:
  200:
    content:
      - id: integer
      - name: string
      - breed: string
      - age: integer
      - weight: float
      - size: string
      - description: string
      - image_url: string
```

#### Get Pet Detail
```yaml
GET /api/pets/{pet_id}/
Description: 특정 반려동물의 상세 정보 조회
Responses:
  200: 반려동물 정보 제공
  404: 반려동물 없음
```

#### Update Pet
```yaml
PUT /api/pets/{pet_id}/
Description: 반려동물 정보 수정
Request Body:
  - name: string (optional)
  - breed: string (optional)
  - age: integer (optional)
  - weight: float (optional)
  - size: string (optional)
  - description: string (optional)
Responses:
  200: 수정 성공
  404: 반려동물 없음
```

#### Delete Pet
```yaml
DELETE /api/pets/{pet_id}/
Description: 반려동물 정보 삭제
Responses:
  204: 삭제 성공
  404: 반려동물 없음
```


### Pets API (추가)

#### Pet Image Upload
```yaml
POST /api/pets/{pet_id}/image/
Description: 반려동물 이미지 업로드
Request Body:
  - image: file (required)
Responses:
  200: 이미지 업로드 성공
  400: 잘못된 요청
```

#### Pet Soft Delete
```yaml
DELETE /api/pets/{pet_id}/soft-delete/
Description: 반려동물 정보 소프트 삭제
Responses:
  204: 소프트 삭제 성공
  404: 반려동물 없음
```

## 3. Posts API

### Post APIs
#### Create Post
```yaml
POST /api/posts/
Description: 새로운 게시글 작성
Request Body:
  - title: string (required)
  - content: string (required)
  - category: string (required)
  - district: string (required)
  - neighborhood: string (optional)
Responses:
  201: 게시글 생성 성공
  400: 잘못된 요청
```

#### Get Post List
```yaml
GET /api/posts/
Description: 게시글 목록 조회
Responses:
  200:
    content:
      - id: integer
      - title: string
      - content: string
      - author: object
        - id: integer
        - nickname: string
      - category: string
      - created_at: datetime
```

#### Get Post Detail
```yaml
GET /api/posts/{post_id}/
Description: 특정 게시글 상세 조회
Responses:
  200: 게시글 정보 제공
  404: 게시글 없음
```

#### Toggle Like
```yaml
POST /api/posts/{post_id}/like/
Description: 게시글 좋아요/취소
Responses:
  200: 상태 변경 성공
  404: 게시글 없음
```

#### Report Post
```yaml
POST /api/posts/{post_id}/report/
Description: 게시글 신고
Request Body:
  - reason: string (required)
  - description: string (optional)
Responses:
  201: 신고 성공
  400: 잘못된 요청
```

### Posts API (추가)

#### Create Comment
```yaml
POST /api/posts/{post_id}/comments/
Description: 게시글에 댓글 작성
Request Body:
  - content: string (required)
Responses:
  201: 댓글 생성 성공
  400: 잘못된 요청
```
아래는 네 가지 앱(`direct messages`, `friends`, `notices`, `notifications`)에 대한 Swagger 스타일의 API 명세서입니다. 각 엔드포인트의 주요 기능을 포함하여 작성했습니다.

### 4. Direct Messages API

#### Create Message
```yaml
POST /api/messages/
Description: 새로운 메시지 생성
Request Body:
  - receiver: integer (required) - 수신자 ID
  - content: string (required, max_length=500) - 메시지 내용
Responses:
  201: 메시지 생성 성공
  400: 잘못된 요청 (자기 자신에게 메시지 전송 불가)
```

#### Get Message List
```yaml
GET /api/messages/
Description: 메시지 목록 조회
Responses:
  200:
    content:
      - id: integer
      - content: string
      - sender_nickname: string
      - receiver_nickname: string
      - created_at: datetime
      - is_read: boolean
```

#### Get Received Messages
```yaml
GET /api/messages/received/
Description: 수신된 메시지 목록 조회
Responses:
  200: 수신 메시지 목록
```

#### Get Sent Messages
```yaml
GET /api/messages/sent/
Description: 발신한 메시지 목록 조회
Responses:
  200: 발신 메시지 목록
```

#### Mark Message as Read
```yaml
PUT /api/messages/{message_id}/read/
Description: 메시지 읽음 표시
Responses:
  200: 읽음 처리 성공
  404: 메시지 없음
```

#### Delete Message
```yaml
DELETE /api/messages/{message_id}/
Description: 메시지 삭제
Responses:
  204: 삭제 성공
  404: 메시지 없음
```

#### Bulk Delete Messages
```yaml
POST /api/messages/bulk-delete/
Description: 여러 메시지 삭제
Request Body:
  - message_ids: array[integer]
Responses:
  204: 삭제 성공
  400: 잘못된 요청
```

### 5. Friends API

#### Send Friend Request
```yaml
POST /api/friends/request/
Description: 친구 요청 보내기
Request Body:
  - to_user: integer (required) - 친구 요청 받을 사용자 ID
Responses:
  201: 친구 요청 성공
  400: 잘못된 요청
```

#### Accept/Reject Friend Request
```yaml
PUT /api/friends/{friend_id}/
Description: 친구 요청 수락/거절
Request Body:
  - status: string (required) - 'accepted' or 'rejected'
Responses:
  200: 상태 변경 성공
  404: 요청 없음
```

#### Get Friend List
```yaml
GET /api/friends/
Description: 친구 목록 조회
Responses:
  200:
    content:
      - id: integer
      - friend: object
        - id: integer
        - nickname: string
      - status: string
```

### 6. Notices API

#### Create Notice
```yaml
POST /api/notices/
Description: 공지사항 생성 (관리자 전용)
Request Body:
  - title: string (required)
  - content: string (required)
  - is_pinned: boolean
  - images: array[file]
  - files: array[file]
Responses:
  201: 공지사항 생성 성공
  403: 권한 없음
```

#### Get Notice List
```yaml
GET /api/notices/
Description: 공지사항 목록 조회
Query Parameters:
  - search: string - 검색어
  - is_pinned: boolean - 상단고정 여부
Responses:
  200:
    content:
      - id: integer
      - title: string
      - author_nickname: string
      - created_at: datetime
      - views: integer
```

#### Get Notice Detail
```yaml
GET /api/notices/{notice_id}/
Description: 특정 공지사항 상세 조회
Responses:
  200: 공지사항 정보 제공
  404: 공지사항 없음
```

#### Download Notice File
```yaml
GET /api/notices/{notice_id}/files/{file_id}/
Description: 공지사항 첨부파일 다운로드
Responses:
  200: 파일 다운로드
  404: 파일 없음
```

### 7. Notifications API

#### Get Notifications
```yaml
GET /api/notifications/
Description: 알림 목록 조회
Responses:
  200:
    content:
      - id: integer
      - title: string
      - message: string
      - notification_type: string
      - is_read: boolean
      - created_at: datetime
```

#### Mark Notification as Read
```yaml
POST /api/notifications/{notification_id}/read/
Description: 알림 읽음 처리
Responses:
  200: 읽음 처리 성공
  404: 알림 없음
```

#### Update Notification Settings
```yaml
PUT /api/notifications/settings/
Description: 알림 설정 변경
Request Body:
  - push_enabled: boolean
  - message_notification: boolean
  - comment_notification: boolean
Responses:
  200: 설정 변경 성공
```

#### Create Web Push Subscription
```yaml
POST /api/notifications/web-push/
Description: 웹 푸시 구독 생성
Request Body:
  - endpoint: string
  - keys:
      p256dh: string
      auth: string
Responses:
  200: 구독 생성 성공
  400: 잘못된 요청
```

#### Delete Web Push Subscription
```yaml
DELETE /api/notifications/web-push/
Description: 웹 푸시 구독 삭제
Request Body:
  - endpoint: string
Responses:
  204: 삭제 성공
  404: 구독 없음
```


## 8. 고객센터 API

### 1.1 문의하기
- **Endpoint**: `POST /api/v1/customer-service/inquiries`
- **Description**: 고객 문의 메일 전송
- **Request Body**:
```json
{
    "title": "string",     // 필수, 제목
    "email": "string",     // 필수, 이메일
    "address": {
        "district": "string",      // 필수, 구
        "neighborhood": "string",   // 필수, 동
        "custom_address": "string" // 선택, 직접 입력 주소
    },
    "content": "string"    // 필수, 문의 내용
}
```
- **Response (201 Created)**:
```json
{
    "inquiry_id": 1,
    "title": "서비스 이용 문의",
    "email": "user@example.com",
    "status": "submitted",
    "created_at": "2024-12-04T15:00:00Z"
}
```
- **Error Response**:
```json
{
    "error": "VALIDATION_ERROR",
    "message": "필수 입력값이 누락되었습니다",
    "details": {
        "title": ["이 필드는 필수입니다."]
    }
}
```
## 9. Weather API

### Weather APIs
#### Get Current Weather
```yaml
GET /api/weather/current/
Description: 현재 날씨 정보 조회
Query Parameters:
  - district: string (required)
Responses:
  200:
    content:
      - district: string
      - neighborhood: string
      - temperature: float
      - humidity: float
      - wind_speed: float
      - precipitation: float
      - precipitation_type: string
      - walking_score: integer
      - forecast_time: datetime
  404: 날씨 데이터 없음
```




## 날씨 API 수정용 초안 - 적합한 외부 api 탐색중

### 1.1 현재 날씨 조회
- **Endpoint**: `GET /api/weather/current`
- **Description**: 현재 날씨 정보와 산책 추천 정보 조회
- **Query Parameters**:
  - district: 구 이름 (필수)
  - neighborhood: 동 이름 (필수)
- **Response (200 OK)**:
```json
{
    "location": {
        "district": "string",
        "neighborhood": "string"
    },
    "current_weather": {
        "condition": {
            "code": "string",      // WEATHER_CONDITIONS 코드
            "name": "string"       // 날씨 상태 한글명
        },
        "temperature": "float",    // 온도 (°C)
        "wind_speed": "float",     // 풍속 (m/s)
        "fine_dust": {
            "level": "string",     // FINE_DUST_LEVELS 코드
            "name": "string",      // 미세먼지 등급 한글명
            "value": "integer"     // 미세먼지 수치 (μg/m³)
        },
        "precipitation": {
            "amount": "float",     // 강수량 (mm)
            "probability": "integer", // 강수확률 (%)
            "type": "string"       // 강수 유형 (비/눈/이슬비)
        }
    },
    "walking_info": {
        "score": "integer",        // 산책 점수 (0-100)
        "recommendation": "string", // 산책 추천 메시지
        "warning": "string"        // 주의사항 (있는 경우)
    },
    "forecast_time": "datetime",   // 날씨 데이터 측정 시간
    "updated_at": "datetime"       // 데이터 갱신 시간
}
```

- **Error Response (400 Bad Request)**:
```json
{
    "error": "INVALID_PARAMETERS",
    "message": "구와 동 정보가 필요합니다"
}
```

- **Error Response (404 Not Found)**:
```json
{
    "error": "DATA_NOT_FOUND",
    "message": "해당 지역의 날씨 정보를 찾을 수 없습니다"
}
```

### 1.2 날씨 상태 코드
```python
WEATHER_CONDITIONS = {
    'HEAVY_RAIN': '폭우',
    'RAIN': '비',
    'FINE_DUST_BAD': '미세먼지 나쁨',
    'FINE_DUST_VERY_BAD': '미세먼지 매우 나쁨',
    'COLD_WAVE': '한파',
    'HEAT_WAVE': '폭염',
    'CLEAR': '맑음',
    'PARTLY_CLOUDY': '구름 조금',
    'CLOUDY': '흐림',
    'SNOW': '눈',
    'DRIZZLE': '이슬비',
    'DEFAULT': '일반'
}

FINE_DUST_LEVELS = {
    'VERY_GOOD': '매우좋음',
    'GOOD': '좋음',
    'MODERATE': '보통',
    'BAD': '나쁨',
    'VERY_BAD': '매우나쁨'
}
```

### 1.3 산책 점수 계산 기준
```python
WALKING_SCORE_CRITERIA = {
    'temperature': {
        'optimal': (15, 25),   # 최적 온도 범위
        'acceptable': (10, 30) # 수용 가능 온도 범위
    },
    'wind_speed': {
        'light': 5,           # 약한 바람
        'strong': 10          # 강한 바람
    },
    'precipitation': {
        'light': 1,           # 약한 강수
        'heavy': 5            # 강한 강수
    }
}
```