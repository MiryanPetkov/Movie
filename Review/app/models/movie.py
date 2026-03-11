from pydantic import BaseModel, Field, field_validator, ConfigDict  # 👈 Променен import
from datetime import datetime
from typing import Optional

class MovieCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    director: str = Field(..., min_length=1, max_length=50)
    release_year: int
    
    @field_validator('release_year')
    @classmethod
    def validate_year(cls, v: int) -> int:
        current_year = datetime.now().year
        if v < 1888 or v > current_year + 1:
            raise ValueError(f'Release year must be between 1888 and {current_year + 1}')
        return v
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Title cannot be empty')
        return v
    
    @field_validator('director')
    @classmethod
    def validate_director(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Director cannot be empty')
        return v

class MovieUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    director: Optional[str] = Field(None, min_length=1, max_length=50)
    release_year: Optional[int] = None
    
    @field_validator('release_year')
    @classmethod
    def validate_year(cls, v: Optional[int]) -> Optional[int]:
        if v is not None:
            current_year = datetime.now().year
            if v < 1888 or v > current_year + 1:
                raise ValueError(f'Release year must be between 1888 and {current_year + 1}')
        return v
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('Title cannot be empty')
        return v
    
    @field_validator('director')
    @classmethod
    def validate_director(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('Director cannot be empty')
        return v

class MovieResponse(BaseModel):
    id: int
    title: str
    director: str
    release_year: int
    rating: Optional[float] = None
    enrichment_status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)