"""
ORIONIS Database Models - Core Entities
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Integer, JSON, Enum, Float, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
import enum
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


def generate_uuid():
    return str(uuid.uuid4())


# ============== ENUMS ==============

class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class TenantPlan(str, enum.Enum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class RoleType(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class AgentStatus(str, enum.Enum):
    ACTIVE = "active"
    STANDBY = "standby"
    DISABLED = "disabled"


class IntegrationStatus(str, enum.Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class AutomationStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


# ============== USERS ==============

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # Null for OAuth users
    name = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    language = Column(String(10), default="pt-BR")
    timezone = Column(String(50), default="America/Sao_Paulo")
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    is_verified = Column(Boolean, default=False)
    
    # 2FA
    two_factor_secret = Column(String(32), nullable=True)
    two_factor_enabled = Column(Boolean, default=False)
    
    # OAuth
    oauth_provider = Column(String(50), nullable=True)
    oauth_id = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    memberships = relationship("Membership", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")


class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token = Column(String(255), unique=True, nullable=True)
    device_info = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    user = relationship("User", back_populates="sessions")


class ApiKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    key_hash = Column(String(255), nullable=False)
    key_prefix = Column(String(20), nullable=False)  # For identification
    scopes = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    user = relationship("User", back_populates="api_keys")
    tenant = relationship("Tenant", back_populates="api_keys")


# ============== TENANTS ==============

class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    logo_url = Column(String(500), nullable=True)
    domain = Column(String(255), nullable=True, unique=True)
    
    # Branding
    slogan = Column(String(255), nullable=True)
    brand_primary = Column(String(7), default="#00e5ff")
    brand_secondary = Column(String(7), default="#ff9d00")
    
    # AI Customization
    ai_name = Column(String(50), default="ORIONIS")
    ai_persona = Column(Text, nullable=True)
    
    # Plan & Billing
    plan = Column(Enum(TenantPlan), default=TenantPlan.FREE)
    credit_balance = Column(Float, default=0.0)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    # Relationships
    memberships = relationship("Membership", back_populates="tenant", cascade="all, delete-orphan")
    settings = relationship("TenantSettings", back_populates="tenant", uselist=False, cascade="all, delete-orphan")
    ai_settings = relationship("AIModelSettings", back_populates="tenant", uselist=False, cascade="all, delete-orphan")
    security_settings = relationship("SecuritySettings", back_populates="tenant", uselist=False, cascade="all, delete-orphan")
    billing_settings = relationship("BillingSettings", back_populates="tenant", uselist=False, cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="tenant", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="tenant", cascade="all, delete-orphan")
    integrations = relationship("Integration", back_populates="tenant", cascade="all, delete-orphan")
    automations = relationship("Automation", back_populates="tenant", cascade="all, delete-orphan")
    knowledge_documents = relationship("KnowledgeDocument", back_populates="tenant", cascade="all, delete-orphan")


# ============== MEMBERSHIPS & ROLES ==============

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(50), nullable=False)
    type = Column(Enum(RoleType), nullable=False)
    description = Column(String(255), nullable=True)
    is_system = Column(Boolean, default=False)  # System roles can't be deleted
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
    memberships = relationship("Membership", back_populates="role")


class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    key = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    module = Column(String(50), nullable=False)  # e.g., settings, chat, billing
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    role_permissions = relationship("RolePermission", back_populates="permission")


class RolePermission(Base):
    __tablename__ = "role_permissions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    role_id = Column(String(36), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permission_id = Column(String(36), ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)
    
    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="role_permissions")
    
    __table_args__ = (
        Index("ix_role_permission", "role_id", "permission_id", unique=True),
    )


class Membership(Base):
    __tablename__ = "memberships"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(String(36), ForeignKey("roles.id"), nullable=False)
    is_default = Column(Boolean, default=False)  # Default tenant for user
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    user = relationship("User", back_populates="memberships")
    tenant = relationship("Tenant", back_populates="memberships")
    role = relationship("Role", back_populates="memberships")
    
    __table_args__ = (
        Index("ix_membership_user_tenant", "user_id", "tenant_id", unique=True),
    )


# ============== SETTINGS ==============

class UserSettings(Base):
    __tablename__ = "user_settings"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Voice
    voice_enabled = Column(Boolean, default=True)
    voice_name = Column(String(50), default="nova")
    voice_speed = Column(Float, default=1.0)
    voice_auto_response = Column(Boolean, default=False)
    
    # Vision
    camera_enabled = Column(Boolean, default=True)
    ocr_enabled = Column(Boolean, default=True)
    vision_mode = Column(String(20), default="auto")
    
    # Memory
    memory_enabled = Column(Boolean, default=True)
    memory_retention_days = Column(Integer, default=90)
    
    # Notifications
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    user = relationship("User", back_populates="settings")


class TenantSettings(Base):
    __tablename__ = "tenant_settings"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # General
    company_name = Column(String(255), nullable=True)
    company_logo = Column(String(500), nullable=True)
    custom_domain = Column(String(255), nullable=True)
    
    # Features
    automation_enabled = Column(Boolean, default=True)
    knowledge_auto_index = Column(Boolean, default=True)
    website_builder_enabled = Column(Boolean, default=True)
    app_builder_enabled = Column(Boolean, default=True)
    
    # Feature Flags
    feature_flags = Column(JSON, default=dict)
    
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    tenant = relationship("Tenant", back_populates="settings")


class AIModelSettings(Base):
    __tablename__ = "ai_model_settings"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Models
    primary_model = Column(String(50), default="gpt-4o")
    fast_model = Column(String(50), default="gpt-4o-mini")
    vision_model = Column(String(50), default="gpt-4o")
    voice_model = Column(String(50), default="whisper-1")
    tts_model = Column(String(50), default="tts-1")
    image_model = Column(String(50), default="gpt-image-1")
    
    # Parameters
    temperature = Column(Float, default=0.7)
    max_context_tokens = Column(Integer, default=8000)
    response_style = Column(String(20), default="balanced")  # concise, balanced, detailed
    
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    tenant = relationship("Tenant", back_populates="ai_settings")


class SecuritySettings(Base):
    __tablename__ = "security_settings"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    two_factor_required = Column(Boolean, default=False)
    session_timeout_minutes = Column(Integer, default=480)
    allow_api_keys = Column(Boolean, default=True)
    max_api_keys = Column(Integer, default=10)
    audit_log_retention_days = Column(Integer, default=90)
    ip_whitelist = Column(JSON, default=list)
    
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    tenant = relationship("Tenant", back_populates="security_settings")


class BillingSettings(Base):
    __tablename__ = "billing_settings"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    current_plan = Column(Enum(TenantPlan), default=TenantPlan.FREE)
    usage_limit = Column(Integer, default=1000)  # Credits per month
    credit_balance = Column(Float, default=0.0)
    billing_email = Column(String(255), nullable=True)
    stripe_customer_id = Column(String(100), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    tenant = relationship("Tenant", back_populates="billing_settings")


# ============== CHAT ==============

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(255), default="Nova Conversa")
    summary = Column(Text, nullable=True)
    is_archived = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)
    
    # Context
    system_prompt = Column(Text, nullable=True)
    model = Column(String(50), default="gpt-4o")
    temperature = Column(Float, default=0.7)
    
    # Metadata
    total_tokens = Column(Integer, default=0)
    total_messages = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    tenant = relationship("Tenant", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String(20), default="text")  # text, image, audio, file
    
    # Token usage
    tokens_prompt = Column(Integer, default=0)
    tokens_completion = Column(Integer, default=0)
    
    # Agent info
    agent_name = Column(String(50), nullable=True)
    
    # Metadata
    extra_data = Column(JSON, default=dict)
    
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    conversation = relationship("Conversation", back_populates="messages")
    attachments = relationship("MessageAttachment", back_populates="message", cascade="all, delete-orphan")


class MessageAttachment(Base):
    __tablename__ = "message_attachments"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    message_id = Column(String(36), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_url = Column(String(500), nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    message = relationship("Message", back_populates="attachments")


# ============== KNOWLEDGE BASE ==============

class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_url = Column(String(500), nullable=False)
    
    # Processing
    status = Column(String(20), default="pending")  # pending, processing, indexed, error
    chunk_count = Column(Integer, default=0)
    
    # Namespace for organization
    namespace = Column(String(100), default="default")
    
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    tenant = relationship("Tenant", back_populates="knowledge_documents")
    chunks = relationship("KnowledgeChunk", back_populates="document", cascade="all, delete-orphan")


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("knowledge_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    
    content = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True)  # Vector embedding
    chunk_index = Column(Integer, nullable=False)
    
    chunk_meta = Column(JSON, default=dict)
    
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    document = relationship("KnowledgeDocument", back_populates="chunks")


# ============== MEMORY ==============

class Memory(Base):
    __tablename__ = "memories"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    
    content = Column(Text, nullable=False)
    memory_type = Column(String(20), default="general")  # general, preference, fact, context
    importance = Column(Float, default=0.5)
    
    # For retrieval
    embedding = Column(JSON, nullable=True)
    
    access_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


# ============== INTEGRATIONS ==============

class Integration(Base):
    __tablename__ = "integrations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    provider = Column(String(50), nullable=False)  # whatsapp, gmail, slack, etc.
    name = Column(String(100), nullable=False)
    status = Column(Enum(IntegrationStatus), default=IntegrationStatus.DISCONNECTED)
    
    # Encrypted credentials
    credentials = Column(JSON, default=dict)
    
    # Configuration
    config = Column(JSON, default=dict)
    
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    tenant = relationship("Tenant", back_populates="integrations")


# ============== AUTOMATIONS ==============

class Automation(Base):
    __tablename__ = "automations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(AutomationStatus), default=AutomationStatus.ACTIVE)
    
    # Trigger configuration
    trigger_type = Column(String(50), nullable=False)  # schedule, webhook, event
    trigger_config = Column(JSON, default=dict)
    
    # Actions
    actions = Column(JSON, default=list)
    
    # Execution stats
    run_count = Column(Integer, default=0)
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    last_run_status = Column(String(20), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    tenant = relationship("Tenant", back_populates="automations")
    runs = relationship("AutomationRun", back_populates="automation", cascade="all, delete-orphan")


class AutomationRun(Base):
    __tablename__ = "automation_runs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    automation_id = Column(String(36), ForeignKey("automations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    status = Column(String(20), nullable=False)  # running, success, failed
    started_at = Column(DateTime(timezone=True), default=utc_now)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Results
    output = Column(JSON, default=dict)
    error = Column(Text, nullable=True)
    
    automation = relationship("Automation", back_populates="runs")


# ============== AGENTS ==============

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    
    name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    agent_type = Column(String(50), nullable=False)  # core, knowledge, multimodal, builder, operational
    status = Column(Enum(AgentStatus), default=AgentStatus.ACTIVE)
    
    # Configuration
    system_prompt = Column(Text, nullable=True)
    capabilities = Column(JSON, default=list)
    config = Column(JSON, default=dict)
    
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class AgentRun(Base):
    __tablename__ = "agent_runs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    input_data = Column(JSON, default=dict)
    output_data = Column(JSON, default=dict)
    
    status = Column(String(20), nullable=False)  # running, success, failed
    started_at = Column(DateTime(timezone=True), default=utc_now)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    tokens_used = Column(Integer, default=0)
    duration_ms = Column(Integer, default=0)


# ============== ANALYTICS ==============

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    event_type = Column(String(50), nullable=False, index=True)
    event_data = Column(JSON, default=dict)
    
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)


class UsageRecord(Base):
    __tablename__ = "usage_records"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Usage metrics
    chat_messages = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)
    voice_minutes = Column(Float, default=0)
    images_generated = Column(Integer, default=0)
    documents_indexed = Column(Integer, default=0)
    api_calls = Column(Integer, default=0)
    
    # Costs
    total_cost = Column(Float, default=0)
    
    created_at = Column(DateTime(timezone=True), default=utc_now)


# ============== AUDIT LOGS ==============

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(36), nullable=True)
    
    # Details
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True)
