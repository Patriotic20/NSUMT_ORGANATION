from pydantic import BaseModel

class QuizProcessBase(BaseModel):
    id: int
    option: str
    
    

class QuizSubmission(BaseModel):
    quiz_id: int
    questions: list[QuizProcessBase]
    
    

class ResultCreate(BaseModel):
    teacher_id: int
    student_id: int
    group_id: int
    subject_id: int
    quiz_id: int
    correct_answers: int
    incorrect_answers: int
    grade: float
    
    
class UserAnswerCreate(BaseModel):
    user_id: int
    quiz_id: int
    question_id: int
    option: str
    
    
