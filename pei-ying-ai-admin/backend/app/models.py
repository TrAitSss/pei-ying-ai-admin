from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    STAFF = "staff"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True)
    full_name = Column(String(100))
    hashed_password = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.STAFF)
    department = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ========== 需求1：标书/报价单自动生成 ==========

class Template(Base):
    """标书/报价单模板"""
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    template_type = Column(String(50), index=True)  # tender(标书), quotation(报价单)
    description = Column(Text)
    content = Column(Text)  # Jinja2 模板内容
    variables = Column(JSON)  # 变量定义列表
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class GeneratedDocument(Base):
    """已生成的文档（含审批状态）"""
    __tablename__ = "generated_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("templates.id"))
    title = Column(String(300))
    variables_data = Column(JSON)
    file_path = Column(String(500))
    status = Column(String(20), default="draft")  # draft, pending_approval, approved, rejected
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    template = relationship("Template")

# ========== 需求2：采购供应商搜索 ==========

class Supplier(Base):
    """供应商"""
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    contact_person = Column(String(100))
    phone = Column(String(50))
    email = Column(String(100))
    address = Column(Text)
    category = Column(String(100))  # 如：音響設備、辦公家具、清潔用品
    tags = Column(JSON)  # 标签列表
    notes = Column(Text)
    quotation_history = Column(JSON)  # 历史报价记录
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ========== 需求3：消耗品库存计算 ==========

class InventoryItem(Base):
    """库存物品"""
    __tablename__ = "inventory_items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    category = Column(String(50))  # 如：紙張、墨水、文具
    location = Column(String(100))  # 存放位置
    current_quantity = Column(Integer, default=0)
    min_quantity = Column(Integer, default=0)  # 最低库存（低于此数触发预警）
    unit = Column(String(20))  # 如：箱、包、盒
    unit_price = Column(Float)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    notes = Column(Text)
    last_counted_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    supplier = relationship("Supplier")

class InventoryLog(Base):
    """库存变动记录"""
    __tablename__ = "inventory_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("inventory_items.id"))
    change_quantity = Column(Integer)  # 变动数量（正=入库，负=出库）
    previous_quantity = Column(Integer)
    new_quantity = Column(Integer)
    action_type = Column(String(20))  # count(盘点), purchase(采购入库), use(领用出库)
    note = Column(Text)
    recorded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)