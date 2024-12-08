
### 모든 API는 인증된 사용자만 접근 가능(401 Unauthorized)


## 1. Users API

### User Authentication APIs //부분수정함
#### User Signup
```yaml
POST /api/users/signup/
Description: 사용자 회원가입
//새로 추가함
Request Body:
  {
    "email": "string",               // 필수, 이메일
    "password": "string",            // 필수, 비밀번호
    "confirm_password": "string",    // 필수, 비밀번호 확인
    "nickname": "string",            // 필수, 닉네임
    "district": "string",            // 필수, 구
    "neighborhood": "string"         // 필수, 동
}

Responses:
  201: 회원가입 성공
  400: 잘못된 요청
  409: 충돌  //새로추가함
{
    "error": "DUPLICATE_VALUE",
    "message": "이메일 또는 닉네임이 이미 사용 중입니다."
}

```

### 이메일 중복 확인 //새로추가함
```yaml
엔드포인트: POST /api/v1/auth/check-email/
설명: 이메일 중복 확인

Request Body:
{
    "email": "string"    // 필수, 중복 확인할 이메일
}

Responses:
  200 성공:
    {
      "available": true    // 이메일 사용 가능 여부
    }

  400 잘못된 요청:
    {
      "error": "VALIDATION_ERROR",
      "message": "유효한 이메일 형식이 아닙니다."
    }
```

### 닉네임 중복 확인 //새로추가함
```yaml
엔드포인트: `POST /api/v1/auth/check-nickname/`
설명: 닉네임 중복 확인

Request Body:
    {
      "nickname": "string"    // 필수, 중복 확인할 닉네임
    }


Responses:
  200 성공:
    {
      "available": true    // 닉네임 사용 가능 여부
    }

  400 잘못된 요청:
    {
      "error": "VALIDATION_ERROR",
      "message": "닉네임은 2~10자 사이여야 합니다."
    }
```


#### User Detail //부분수정함
```yaml
GET /api/users/me/
Description: 사용자 상세 정보 조회
Responses:
  200:
    content:
      - email: string
      - nickname: string
      - profilePhoto: string // 사용자 프로필 사진 URL
      - additionalPhoto: string // 추가 사용자 사진 URL
      - bio : string
  401: 인증되지 않음
```

#### Update User Detail //부분수정함
```yaml
PUT /api/users/me/
Description: 사용자 정보 수정
Request Body:
  - nickname: string (optional)
  - district: string (optional)
  - neighborhood: string (optional)
  - intro: string (optional) // 사용자 자기소개
  - profilePhoto: file (optional) // 프로필 사진
  - additionalPhoto: file (optional) // 추가 사진
Responses:
  200: 수정 성공
  400: 잘못된 요청:
    {
      "error": "INVALID_FILE",
      "message": "파일 형식은 JPEG 또는 PNG여야 하며, 크기는 5MB 이하이어야 합니다."
    }
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
#### Create Pet //부분수정함
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
      - gender: string // 반려동물 성별
      - photo: string // 반려동물 사진 URL
      - additionalPhoto: string // 추가 사진 URL
```

#### Get Pet Detail
```yaml
GET /api/pets/{pet_id}/
Description: 특정 반려동물의 상세 정보 조회
Responses:
  200: 반려동물 정보 제공
  404: 반려동물 없음
```

#### Update Pet  //부분수정함
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
  - gender: string (optional) // 반려동물 성별
  - photo: file (optional) // 반려동물 사진
  - additionalPhoto: file (optional) // 추가 사진
Responses:
  200: 수정 성공
  400: 잘못된 요청
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

### 좋아요한 게시물 목록 조회 (추가)
```yaml
GET /api/posts/liked/
Description: 사용자가 좋아요한 게시물 목록 조회
Responses:
  200: 상태 변경 성공
      {
           "posts": [
              {
                  "id": 1,
                  "category": "string",
                  "title": "string",
                  "created_at": "datetime"
              }
          ]
      }

  401: 인증되지 않음
  404: 게시물 없음
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
  400: 잘못된 요청 (예: 수신자 ID 없음, 메시지 내용이 비어 있음) //수정완료
  401: 인증 실패 (로그인 필요) //수정완료
  500: 서버 에러 //수정완료
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
      - sender.nickname: string  // _을 .으로 수정
      - receiver.nickname: string // _을 .으로 수정
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

#### Bulk Delete Messages   //싹 삭제 불필요
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

#### Delete Friend  //새로추가함 (참고 : 쪽지 버튼 누르면 모달창 생성 후 입력 후 답장 전송 가능)
```yaml
PUT /api/friends/{friend_id}/
Description: 친구 삭제
Request Body:
  - status: string (required) - 'rejected'
Responses:
  200: 친구 삭제 성공
  404: 친구 없음
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
// 선택, 직접 입력 주소 삭제 <br/>
// (참고 이메일의 경우 : 아이디만 입력 + 도메인 선택(없을 시 직접입력))
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
# Weather API 문서

## 현재 날씨 조회 API
현재 서울 지역의 실시간 날씨 정보를 제공합니다.

**Endpoint**: `GET /api/weathers/current/`

### 응답 형식
```json
{
    "temperature": 8.81,         // 온도(°C)
    "humidity": 42,             // 습도(%)
    "wind_speed": 6.81,         // 풍속(m/s)
    "precipitation_probability": 0, // 강수확률(%)
    "weather_code": 1000        // 날씨코드
}
```

### 날씨 코드 정의
| 코드 | 설명 |
|------|------|
| 1000 | 맑음 |
| 1001 | 흐림 |
| 1100 | 대체로 맑음 |
| 2000 | 안개 |
| 2100 | 옅은 안개 |
| 4000 | 이슬비 |
| 4001 | 비 |
| 4200 | 강한 비 |

### 에러 응답
```json
{
    "error": "error message"
}
```

### 응답 코드
- 200: 성공
- 500: 서버 에러

### 참고사항
- 위치 정보는 서울(위도: 37.5665, 경도: 126.9780)로 고정되어 있습니다
- 온도는 섭씨 단위로 제공됩니다
- 풍속은 m/s 단위로 제공됩니다

### 파일 업로드 관련 주의사항
- 모든 업로드된 파일은 다음 조건을 만족해야 합니다:
    - 최대 크기: 5MB
    - 허용 형식: JPEG, PNG
- 잘못된 파일 형식 또는 크기 초과 시:
    ```
    {
        "error": "INVALID_FILE",
        "message": "파일 형식은 JPEG 또는 PNG여야 하며, 크기는 5MB 이하이어야 합니다."
    }
    
    ```
    
---
