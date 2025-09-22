from fastapi import APIRouter

from auth.api import router as auth_router
from user.api import router as user_router

from department.api import router as department_router
from worker.api import router as worker_router

from faculty.api import router as faculty_router
from chair.api import router as chair_router
from group.api import router as group_router

from teacher.api import router as teacher_router
from student.api import router as student_router


from role.api import router as role_router

from permission.api import router as perm_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(user_router)

router.include_router(department_router)
router.include_router(worker_router)

router.include_router(faculty_router)
router.include_router(chair_router)
router.include_router(group_router)

router.include_router(teacher_router)
router.include_router(student_router)

router.include_router(role_router)

router.include_router(perm_router)


