# AGENT.md

## 프로젝트 개요

이 프로젝트는 FastAPI(백엔드)와 Next.js(프론트엔드)로 구축하는 "파이보(Pybo)"라는 이름의 질문/답변 게시판 서비스다. 회원 인증, 질문 및 답변 CRUD, 페이징, 검색, 마크다운 렌더링, 추천 기능을 갖춘 풀스택 웹 애플리케이션을 구현하는 것이 목표다.

---

## 기술 스택

### 백엔드
- **런타임**: Python 3.11+
- **프레임워크**: FastAPI
- **ORM**: SQLAlchemy
- **데이터베이스**: SQLite (개발), PostgreSQL (운영)
- **마이그레이션**: Alembic
- **유효성 검사**: Pydantic v2
- **인증**: JWT (python-jose), 비밀번호 해시 (passlib + bcrypt)
- **서버**: Uvicorn (개발), Gunicorn + UvicornWorker (운영)
- **리버스 프록시**: Nginx

### 프론트엔드
- **프레임워크**: Next.js 14+ (App Router)
- **언어**: TypeScript
- **스타일링**: Tailwind CSS
- **상태 관리**: Zustand (원서의 Svelte 스토어를 대체)
- **HTTP 클라이언트**: Axios 또는 fetch (커스텀 훅 활용)
- **마크다운**: react-markdown + remark-gfm

### 인프라
- **버전 관리**: Git + GitHub
- **배포**: AWS Lightsail (Ubuntu)
- **SSL**: Let's Encrypt (Certbot)

---

## 프로젝트 구조

```
project-root/
  backend/
    main.py
    database.py
    models.py
    domain/
      question/
        question_router.py
        question_schema.py
        question_crud.py
      answer/
        answer_router.py
        answer_schema.py
        answer_crud.py
      user/
        user_router.py
        user_schema.py
        user_crud.py
    migrations/
    myapi.db
  frontend/
    app/
      layout.tsx
      page.tsx
      question/
        page.tsx
        [id]/
          page.tsx
      auth/
        login/
          page.tsx
        signup/
          page.tsx
    components/
      Navigation.tsx
      QuestionList.tsx
      QuestionDetail.tsx
      AnswerForm.tsx
      Pagination.tsx
      MarkdownEditor.tsx
    lib/
      api.ts
      auth.ts
    store/
      authStore.ts
    types/
      index.ts
```

---

## 백엔드 아키텍처

### 애플리케이션 진입점 (`main.py`)

- FastAPI 앱 인스턴스 생성
- 모든 도메인 라우터를 `/api` 프리픽스로 등록
- Next.js 프론트엔드(`http://localhost:3000`)의 요청을 허용하도록 CORS 설정
- 필요한 경우 lifespan 컨텍스트로 시작/종료 이벤트 처리

### 데이터베이스 (`database.py`)

- 데이터베이스 URL로 SQLAlchemy 엔진 설정
- 세션 관리를 위한 `SessionLocal`과 `get_db` 의존성 정의
- 모델 상속을 위한 `Base = declarative_base()` 선언

### 모델 (`models.py`)

다음 SQLAlchemy ORM 모델을 정의한다.

**Question (질문)**
- `id`: Integer, 기본 키
- `subject`: String, not null
- `content`: Text, not null
- `create_date`: DateTime, not null
- `modify_date`: DateTime, nullable
- `user_id`: User 테이블 외래 키
- `user`: User 관계
- `answers`: Answer 목록 관계
- `voter`: User와의 다대다 관계 (추천 기능용)

**Answer (답변)**
- `id`: Integer, 기본 키
- `content`: Text, not null
- `create_date`: DateTime, not null
- `modify_date`: DateTime, nullable
- `question_id`: Question 테이블 외래 키
- `user_id`: User 테이블 외래 키
- `user`: User 관계
- `voter`: User와의 다대다 관계

**User (사용자)**
- `id`: Integer, 기본 키
- `username`: String, unique, not null
- `password`: String, not null
- `email`: String, unique, not null

### 도메인 구조

각 도메인(`question`, `answer`, `user`)은 다음 3계층 패턴을 따른다.

1. **라우터** (`*_router.py`): API 엔드포인트 정의, HTTP 요청/응답 처리
2. **스키마** (`*_schema.py`): 입력 유효성 검사 및 출력 직렬화를 위한 Pydantic 모델
3. **CRUD** (`*_crud.py`): 라우터 로직과 분리된 데이터베이스 접근 로직

### 의존성 주입

- `get_db`: 요청마다 데이터베이스 세션을 yield하며, 라우터에서 `Depends(get_db)`로 사용
- `get_current_user`: JWT 토큰을 디코딩하여 인증된 사용자를 반환하며, 보호된 엔드포인트에서 `Depends(get_current_user)`로 사용

### 인증

- 로그인 시 JWT 액세스 토큰 발급 (`/api/user/login`)
- 토큰 형식: `{ "sub": username, "exp": 만료시각 }`
- 토큰 생성 및 검증에 `OAuth2PasswordBearer`와 `python-jose` 사용
- 비밀번호는 `passlib`의 bcrypt로 해시 처리

### API 엔드포인트

**질문 (Question)**
- `GET /api/question/list` - 질문 목록 조회 (페이징, 검색 지원)
  - 쿼리 파라미터: `page`, `size`, `keyword`
  - 응답: `{ total, question_list }`
- `GET /api/question/detail/{question_id}` - 질문 상세 조회
- `POST /api/question/create` - 질문 등록 (인증 필요)
- `PUT /api/question/update` - 질문 수정 (인증 필요, 작성자 본인만)
- `DELETE /api/question/delete` - 질문 삭제 (인증 필요, 작성자 본인만)
- `POST /api/question/vote` - 질문 추천 (인증 필요)

**답변 (Answer)**
- `POST /api/answer/create/{question_id}` - 답변 등록 (인증 필요)
- `PUT /api/answer/update` - 답변 수정 (인증 필요, 작성자 본인만)
- `DELETE /api/answer/delete` - 답변 삭제 (인증 필요, 작성자 본인만)
- `POST /api/answer/vote` - 답변 추천 (인증 필요)

**사용자 (User)**
- `POST /api/user/create` - 회원가입
- `POST /api/user/login` - 로그인 (JWT 토큰 반환)

### Alembic 마이그레이션

- `migrations/` 디렉터리에 Alembic 초기화
- `env.py`에서 `models.py`의 `Base`를 임포트하도록 설정
- 모델 변경 후 마이그레이션 파일 생성: `alembic revision --autogenerate -m "설명"`
- 마이그레이션 적용: `alembic upgrade head`

---

## 프론트엔드 아키텍처 (Next.js)

### App Router 구조

- 서버 컴포넌트와 클라이언트 컴포넌트를 활용하는 App Router (`app/` 디렉터리) 사용
- `layout.tsx`: Navigation 컴포넌트를 포함한 루트 레이아웃
- 루트 `page.tsx`: 질문 목록으로 리다이렉트하거나 직접 렌더링

### 페이지

- `/` 또는 `/question`: 페이징 및 검색이 적용된 질문 목록
- `/question/[id]`: 질문 상세, 답변 목록, 답변 작성 폼
- `/auth/login`: 로그인 폼
- `/auth/signup`: 회원가입 폼

### API 통신 (`lib/api.ts`)

- FastAPI 백엔드를 `baseURL`로 설정한 Axios 인스턴스(또는 fetch 래퍼) 생성
- Zustand 스토어의 JWT 토큰을 보호된 요청의 `Authorization: Bearer <토큰>` 헤더에 첨부
- 401 응답 시 인증 상태를 초기화하고 로그인 페이지로 리다이렉트

### 인증 상태 관리 (`store/authStore.ts`)

- Zustand로 인증 상태 관리: `{ username, token, isLoggedIn }`
- 토큰을 `localStorage`에 저장하고 앱 로드 시 복원(rehydrate)
- `login(token, username)`과 `logout()` 액션 제공
- 원서의 Svelte `writable` 스토어를 대체

### 컴포넌트

**Navigation.tsx**
- 홈 링크가 포함된 사이트 제목/로고 표시
- 비로그인 상태: 로그인/회원가입 링크 표시
- 로그인 상태: 사용자명과 로그아웃 버튼 표시

**QuestionList.tsx**
- 질문 목록을 표로 렌더링: 번호, 제목, 답변 수, 작성자, 작성일
- `keyword` 쿼리 파라미터를 업데이트하는 검색 입력창 포함
- 하단에 Pagination 컴포넌트 포함

**Pagination.tsx**
- `total`, `page`, `size` props 수신
- 전체 페이지 수를 계산하여 페이지 버튼 렌더링
- 페이지 변경 시 URL 쿼리 파라미터 업데이트 (`useRouter` 또는 `<Link>` 활용)

**QuestionDetail.tsx**
- 질문의 제목, 내용(마크다운), 작성자, 작성일, 추천 수 렌더링
- 현재 사용자가 작성자인 경우 수정/삭제 버튼 표시
- 답변 목록도 동일한 방식으로 렌더링
- 하단에 AnswerForm 포함

**AnswerForm.tsx**
- 마크다운을 지원하는 답변 내용 텍스트에어리어
- `POST /api/answer/create/{question_id}` 호출하는 등록 버튼
- 비로그인 상태면 로그인 페이지로 리다이렉트

**MarkdownEditor.tsx**
- 마크다운 작성용 텍스트에어리어 입력창
- `react-markdown` + `remark-gfm`으로 렌더링하는 미리보기 패널

### 게시물 일련번호

- 표시 번호 계산식: `total - ((page - 1) * size) - index`
- 페이지가 바뀌어도 일관된 번호가 유지됨

### 날짜 표시

- ISO 날짜 문자열 포맷에 `date-fns` 또는 기본 `Intl.DateTimeFormat` 활용
- 표시 형식: `YYYY-MM-DD HH:mm:ss`

---

## 주요 기능

### 페이징

- 백엔드는 `page`(0부터 시작)와 `size` 파라미터를 받음
- 백엔드 응답: `{ total: int, question_list: [...] }`
- 프론트엔드가 페이지 수를 계산하고 페이지 내비게이션 렌더링

### 검색

- 백엔드에서 제목 또는 내용에 키워드가 포함된 질문을 필터링
- 프론트엔드는 `keyword`를 쿼리 파라미터로 전달
- 검색 범위: 질문 제목, 질문 내용, 답변 내용

### 추천

- User와 Question/Answer 간의 다대다 관계를 voter 테이블로 구현
- 자신의 게시물은 추천 불가
- 질문 상세 및 답변 목록에 추천 수 표시

### 마크다운

- 사용자가 마크다운 형식으로 내용 작성
- 프론트엔드에서 `react-markdown`과 `remark-gfm`(표, 취소선 등 지원)으로 렌더링

### 인증 흐름

1. 사용자가 `POST /api/user/login`에 자격증명 전송
2. 백엔드가 `{ access_token, token_type }` 반환
3. 프론트엔드가 토큰을 Zustand 스토어에 저장 (localStorage에 영속)
4. 이후 모든 보호된 API 요청에 `Authorization: Bearer <토큰>` 헤더 포함
5. 로그아웃 시 스토어 및 localStorage 초기화

---

## 개발 환경 설정

### 백엔드

```bash
cd backend
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install fastapi uvicorn sqlalchemy alembic pydantic[email] \
            python-jose[cryptography] passlib[bcrypt] python-multipart

alembic upgrade head
uvicorn main:app --reload
```

백엔드 실행 주소: `http://localhost:8000`
Swagger UI: `http://localhost:8000/docs`

### 프론트엔드

```bash
cd frontend
npm install
npm run dev
```

프론트엔드 실행 주소: `http://localhost:3000`

### 환경 변수

**백엔드** (`.env`):
```
DATABASE_URL=sqlite:///./myapi.db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

**프론트엔드** (`.env.local`):
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

## 운영 배포

### 서버 구성

```
클라이언트 -> Nginx -> Gunicorn (UvicornWorker) -> FastAPI
                    -> Next.js (standalone 또는 Node 서버)
```

### 배포 절차

1. GitHub에 코드 Push
2. AWS Lightsail(Ubuntu) 서버에서 Pull
3. Next.js 빌드: `npm run build`
4. Gunicorn으로 FastAPI 실행:
   ```bash
   gunicorn --bind unix:/tmp/myapi.sock main:app \
     --worker-class uvicorn.workers.UvicornWorker
   ```
5. Nginx에서 `/api/` 경로는 Gunicorn 소켓으로, 나머지 경로는 Next.js 서버로 프록시 설정
6. Certbot(Let's Encrypt)으로 SSL 적용
7. 데이터베이스를 SQLite에서 PostgreSQL로 전환:
   - `psycopg2-binary` 설치
   - 환경 변수의 `DATABASE_URL` 업데이트
   - `alembic upgrade head` 실행

### Nginx 설정 예시

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /api/ {
        proxy_pass http://unix:/tmp/myapi.sock;
        include proxy_params;
    }

    location / {
        proxy_pass http://localhost:3000;
        include proxy_params;
    }
}
```

---

## 코드 컨벤션

### 백엔드

- 도메인 주도 구조를 따른다. 각 도메인 디렉터리에 router, schema, crud 파일을 둔다.
- 비즈니스 로직은 라우터가 아닌 CRUD 파일에 작성한다.
- 데이터베이스 세션은 반드시 `Depends(get_db)`를 사용한다. 라우터에서 세션을 직접 생성하지 않는다.
- 모든 요청 바디와 응답 모델에 Pydantic 스키마를 사용한다. ORM 객체를 그대로 반환하지 않는다.
- 쓰기 엔드포인트는 `Depends(get_current_user)`로 보호한다.
- 수정 및 삭제 전에 반드시 소유권(작성자 본인 여부)을 검증한다.

### 프론트엔드

- 모든 파일에 TypeScript를 사용한다.
- 공유 타입은 `types/index.ts`에 정의한다.
- API 호출 로직은 `lib/api.ts`에 모은다. 컴포넌트 내에서 직접 fetch/axios를 호출하지 않는다.
- Zustand는 전역 인증 상태에만 사용한다. 컴포넌트 로컬 상태는 React의 `useState`를 사용한다.
- 가능한 경우 서버 컴포넌트에서 데이터를 fetching한다. 상호작용이 필요한 경우에만 `"use client"`를 선언한다.
- 내부 링크에는 반드시 Next.js의 `<Link>`를 사용한다. `<a>` 태그를 직접 사용하지 않는다.

---

## 참고 사항

- 원서(점프 투 FastAPI)는 프론트엔드로 Svelte를 사용한다. 이 프로젝트는 Svelte를 Next.js App Router로 대체한다. Svelte 고유 패턴(writable 스토어, Svelte 라우터, `$:` 반응성)은 모두 Next.js 및 React 동등 패턴으로 교체된다.
- Svelte의 인증 스토어는 localStorage에 영속되는 Zustand 스토어로 대체된다.
- Svelte 라우팅(`page.js` / 해시 라우팅)은 Next.js App Router의 파일 기반 라우팅으로 대체된다.
- 쿼리 문자열 생성에 사용하던 Svelte의 `qs` 라이브러리는 `URLSearchParams` 또는 Next.js의 `useSearchParams`로 대체된다.