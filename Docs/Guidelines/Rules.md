# 브랜치 규칙

## 브랜치 명명 규칙
`<type>/<issue-number>-<description>`

## 브랜치 유형
- feature: 새로운 기능
- bugfix: 버그 수정
- hotfix: 긴급 수정
- refactor: 리팩토링

## 브랜치 이름 예시
```text
feature/123-implement-user-authentication
bugfix/124-fix-database-connection
hotfix/125-security-vulnerability
```

# 코딩 규칙

## Lint 설정

**pyproject.toml**

```toml
[tool.black]
line-length = 88
target-version = ['py38']
include = '.pyi?$'
extend-exclude = '''
^/foo.py
'''

[tool.isort]
profile = "black"
multilineoutput = 3
includetrailingcomma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
line_length = 88
```

**.flake8**
```text
[tool.flake8]
max-line-length = 88
extend-ignore = E203, W503, F401
exclude = .git,__pycache,build,dist
per-file-ignores = __init.py:F401
```

**.pre-commit-config.yaml**
```text
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        language_version: python3.8

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        name: isort (python)

  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        additional_dependencies: [flake8-docstrings]
```
```
pre-commit run --all-files
```

# 커밋 규칙

## 커밋 메시지 형식
`유형(<scope>): <subject>`

## 커밋 유형
- ✨ feat: 새로운 기능 추가
- 🐛 fix: 기능 수정, 버그 수정
- 💡 chore: 오타 수정, 코드 변경 (주석 추가/수정 포함)
- 📝 docs: 문서 수정
- 🚚 build: 빌드 관련 파일 수정/삭제
- ✅ test: 테스트 코드 추가
- ♻️ refactor: 코드 리팩터링

## 커밋 메시지 예시
- ✨ feat(auth): implement JWT authentication
- 🐛 fix(database): resolve connection timeout issue
- ♻️ refactor(api): optimize user query performance

# Pull Request 규칙

## Pull Request 템플릿
```markdown
## 변경 사항
[구체적인 변경 내용 설명]

## 관련 이슈
[이슈번호]

## 테스트 항목
- [ ] 단위 테스트 통과
- [ ] 통합 테스트 통과
- [ ] 코드 리뷰 완료

## 기타 참고사항
[추가 정보 또는 스크린샷]
```

# 코드 리뷰 규칙

## 기본 원칙
- 최소 1명 이상의 승인 필요
- 24시간 이내 리뷰 진행
- 코드 품질, 테스트 커버리지 확인
- 버그/보안 취약점 검토

## 배포 프로세스
1. 테스트 통과 확인
2. 코드 리뷰 완료
3. CI/CD 파이프라인 통과
4. production 배포

## 환경 구분
- development: 개발/테스트 환경
- production: 운영/배포 환경
