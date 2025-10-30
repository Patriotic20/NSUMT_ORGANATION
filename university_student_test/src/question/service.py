from sqlalchemy.ext.asyncio import AsyncSession
from core.utils.basic_service import BasicService
from .schemas import QuestionCreate, QuestionUpdate
from sqlalchemy import select, insert, and_
from openpyxl import load_workbook
from core.models.questions import Question
from fastapi import HTTPException, status, UploadFile
import tempfile


class QuestionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.service = BasicService(db=session)

    async def create_question(self, question_data: QuestionCreate):
        return await self.service.create(model=Question, obj_items=question_data)

    async def create_question_by_exel(self, subject_id: int, file: UploadFile):
        # Validate file extension
        if not (file.filename.endswith(".xlsx") or file.filename.endswith(".xls")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file format. Please upload an Excel file."
            )

        # Save uploaded file to a temp file
        contents = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp.write(contents)
            temp_path = tmp.name

        # Load Excel workbook
        wb = load_workbook(temp_path)
        sheet = wb.active

        values = []
        for idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            if not row[0]:  # first column = question text
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Row {idx} is invalid: 'text' column is empty"
                )

            values.append({
                "subject_id": subject_id,
                "text": row[0],
                "option_a": row[1],
                "option_b": row[2],
                "option_c": row[3],
                "option_d": row[4],
            })

        # Bulk insert
        stmt = insert(Question).values(values)
        await self.session.execute(stmt)
        await self.session.commit()

        return {"status": "success", "message": f"{len(values)} questions uploaded successfully"}

    async def get_question_by_id(self, question_id: int):
        question = await self.check_by_teacher_id(
            filters=[Question.id == question_id],
            is_all=False
        )
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        return question

    async def get_all_question(self, limit: int = 20, offset: int = 0, teacher_id: int | None = None):
        questions = await self.check_by_teacher_id(
            limit=limit, 
            offset=offset, 
            is_all=True, 
            teacher_id=teacher_id
        )
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No questions found"
            )
        return questions

    async def update_question(self, question_id: int, question_data: QuestionUpdate , teacher_id: int | None = None):
        await self.get_question_by_id(question_id=question_id, teacher_id=teacher_id)
        schema = QuestionUpdate(**question_data.__dict__)
        filters = [Question.id == question_id]
        return await self.service.update(model=Question, filters=filters, update_data=schema)

    async def delete_question(self, question_id: int, teacher_id: int | None = None):
        await self.get_question_by_id(question_id=question_id, teacher_id=teacher_id)
        filters = [Question.id == question_id]
        await self.service.delete(model=Question, filters=filters)
        return {
            "message" : "Delete successfully"
        }
        
    async def check_by_teacher_id(
        self,  
        limit: int | None = None,
        offset: int | None = 0,
        is_all: bool = False,
        filters: list | None = None
    ):
        # Ensure filters is a list
        if filters is None:
            filters = []
            

        # Apply pagination
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset:
            stmt = stmt.offset(offset)

        result = await self.session.execute(stmt)

        data = result.scalars().all() if is_all else result.scalars().all()   
        
        if not data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question not found"
            )
        
        return data
