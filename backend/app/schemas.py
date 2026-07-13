from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    STAFF = "staff"
    TEACHER = "teacher"

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: UserRole = UserRole.STAFF
    department: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class DocumentUpload(BaseModel):
    category: Optional[str] = None

class DocumentResponse(BaseModel):
    id: int
    filename: str
    original_name: Optional[str]
    file_type: Optional[str]
    category: Optional[str]
    status: str
    extracted_text: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class SupplierCreate(BaseModel):
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None

class SupplierResponse(SupplierCreate):
    id: int
    quotation_history: Optional[List[Dict]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class InventoryItemCreate(BaseModel):
    name: str
    category: Optional[str] = None
    location: Optional[str] = None
    current_quantity: int = 0
    min_quantity: int = 0
    unit: Optional[str] = None
    unit_price: Optional[float] = None
    supplier_id: Optional[int] = None
    notes: Optional[str] = None

class InventoryItemResponse(InventoryItemCreate):
    id: int
    last_counted_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class TemplateCreate(BaseModel):
    name: str
    template_type: str
    description: Optional[str] = None
    content: Optional[str] = None
    variables: Optional[List[Dict[str, Any]]] = None

class TemplateResponse(TemplateCreate):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class GenerateDocumentRequest(BaseModel):
    template_id: int
    title: str
    variables_data: Dict[str, Any]

class QAPairCreate(BaseModel):
    question: str
    answer: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    source: Optional[str] = None

class QAPairResponse(QAPairCreate):
    id: int
    usage_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatMessage(BaseModel):
    message: str
    context: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = None
    confidence: Optional[float] = None

class RepairRequestCreate(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    priority: Optional[str] = "normal"

class RepairRequestResponse(RepairRequestCreate):
    id: int
    status: str
    assigned_to: Optional[int]
    submitted_by: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ActivityBudgetCreate(BaseModel):
    activity_name: str
    budget_amount: Optional[float] = None
    actual_income: Optional[float] = None
    actual_expense: Optional[float] = None

class ActivityBudgetResponse(ActivityBudgetCreate):
    id: int
    reconciliation_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class SubstituteRecordCreate(BaseModel):
    absent_teacher: str
    substitute_teacher: str
    subject: Optional[str] = None
    class_name: Optional[str] = None
    date: datetime
    period: Optional[str] = None
    reason: Optional[str] = None

class SubstituteRecordResponse(SubstituteRecordCreate):
    id: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
