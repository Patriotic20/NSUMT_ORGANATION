from pydantic import BaseModel

class QuizProcessBase(BaseModel):
    id: int
    option: str
    
    

class QuizSubmission(BaseModel):
    quiz_id: int
    questions: list[QuizProcessBase]
    
    

class ResultCreate(BaseModel):
    student_id: int
    quiz_id: int
    correct_answers: int
    incorrect_answers: int
    grade: float
    
