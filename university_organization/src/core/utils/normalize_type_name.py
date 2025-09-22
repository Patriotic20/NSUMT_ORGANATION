import re
from fastapi import HTTPException, status

def normalize_type_name(value: str) -> str:
    if not value or not value.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Value cannot be empty"
        ) 
    
    # Trim and lowercase
    value = value.strip().lower()
    
    # Collapse multiple spaces
    value = re.sub(r"\s+", " ", value)
    
    # Add a space if digits/letters are stuck to a word (e.g., "123a-45xyz" -> "123a-45 xyz")
    value = re.sub(r"([0-9]+[a-zA-Z]-[0-9]+)([a-zA-Z]+)", r"\1 \2", value)
    
    # Optionally: separate digit-letter boundaries (e.g., "cs101math" -> "cs101 math")
    value = re.sub(r"(\d)([a-zA-Z])", r"\1 \2", value)
    value = re.sub(r"([a-zA-Z])(\d)", r"\1 \2", value)
    
    return value
