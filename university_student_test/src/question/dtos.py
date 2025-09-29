from fastapi import Form, UploadFile, File

from core.utils.save_file import save_file

class QuestionEnterDto:
    def __init__(
        self,
        subject_id: int = Form(...),
        text: str = Form(None),
        image: UploadFile = File(None),
        option_a: str = Form(None),
        option_a_image: UploadFile = File(None),
        option_b: str = Form(None),
        option_b_image: UploadFile = File(None),
        option_c: str = Form(None),
        option_c_image: UploadFile = File(None),
        option_d: str = Form(None),
        option_d_image: UploadFile = File(None),
    ):
        self.text = text
        
        # auto-save files to disk
        self.image = save_file(image, "questions")
        self.subject_id = subject_id
        self.option_a = option_a
        self.option_a_image = save_file(option_a_image, "questions")
        self.option_b = option_b
        self.option_b_image = save_file(option_b_image, "questions")
        self.option_c = option_c
        self.option_c_image = save_file(option_c_image, "questions")
        self.option_d = option_d
        self.option_d_image = save_file(option_d_image, "questions")


class QuestionUpdateDto:
    def __init__(
        self,
        text: str = Form(None),
        image: UploadFile = File(None),
        option_a: str = Form(None),
        option_a_image: UploadFile = File(None),
        option_b: str = Form(None),
        option_b_image: UploadFile = File(None),
        option_c: str = Form(None),
        option_c_image: UploadFile = File(None),
        option_d: str = Form(None),
        option_d_image: UploadFile = File(None),
    ):
        self.text = text

        # auto-save uploaded files
        self.image = save_file(image, "questions")
        self.option_a = option_a
        self.option_a_image = save_file(option_a_image, "questions")
        self.option_b = option_b
        self.option_b_image = save_file(option_b_image, "questions")
        self.option_c = option_c
        self.option_c_image = save_file(option_c_image, "questions")
        self.option_d = option_d
        self.option_d_image = save_file(option_d_image, "questions")
