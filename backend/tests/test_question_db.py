from datetime import datetime

from app.models.question import Question

def create_question(db_session, subject, content):
    question = Question(
        subject=subject,
        content=content,
        create_date=datetime.now(),
    )

    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    return question


def test_create_question(db_session):
    q1 = create_question(
        db_session,
        subject="pybo가 무엇인가요?",
        content="pybo에 대해서 알고 싶습니다.",
    )

    create_question(
        db_session,
        subject="FastAPI 모델 질문입니다.",
        content="id는 자동으로 생성되나요?",
    )

    saved_question = (
        db_session.query(Question)
        .filter(Question.subject == "pybo가 무엇인가요?")
        .one()
    )

    assert saved_question.id == q1.id
    assert saved_question.content == "pybo에 대해서 알고 싶습니다."


def test_read_question(db_session):
    create_question(
        db_session,
        subject="pybo가 무엇인가요?",
        content="pybo에 대해서 알고 싶습니다.",
    )

    create_question(
        db_session,
        subject="FastAPI 모델 질문입니다.",
        content="id는 자동으로 생성되나요?",
    )

    questions = db_session.query(Question).order_by(Question.id.asc()).all()

    assert len(questions) == 2
    assert questions[0].subject == "pybo가 무엇인가요?"
    assert questions[1].subject == "FastAPI 모델 질문입니다."


def test_read_question_by_id_1(db_session):
    create_question(
        db_session,
        subject="pybo가 무엇인가요?",
        content="pybo에 대해서 알고 싶습니다.",
    )

    # 조건 검색으로 접근할 때 적합
    # question = db_session.query(Question).filter(Question.id == 1).one()

    # PK로 접근할 때 적
    question = db_session.get(Question, 1)

    assert question.id == 1
    assert question.subject == "pybo가 무엇인가요?"
    assert question.content == "pybo에 대해서 알고 싶습니다."


def test_read_question_subject_like_keyword(db_session):
    create_question(
        db_session,
        subject="pybo가 무엇인가요?",
        content="pybo에 대해서 알고 싶습니다.",
    )

    create_question(
        db_session,
        subject="FastAPI 모델 질문입니다.",
        content="id는 자동으로 생성되나요?",
    )

    questions = (
        db_session.query(Question)
        .filter(Question.subject.like("%FastAPI%"))
        .all()
    )

    assert len(questions) == 1
    assert questions[0].subject == "FastAPI 모델 질문입니다."

