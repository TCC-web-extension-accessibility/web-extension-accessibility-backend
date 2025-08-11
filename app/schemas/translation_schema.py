from pydantic import BaseModel
from typing import List

class Translation_schema(BaseModel):
    from_language : str
    text_list : List[str] 
    to_language : str