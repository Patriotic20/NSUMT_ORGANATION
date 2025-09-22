from fastapi import APIRouter
from question.api import router as question_router
from subject.api import router as subject_router
from quiz.api import router as quiz_router
from quiz_process.api import router as quiz_process_router

router = APIRouter()


router.include_router(subject_router)
router.include_router(question_router)
router.include_router(quiz_router)
router.include_router(quiz_process_router)
