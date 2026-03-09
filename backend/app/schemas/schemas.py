"""
ORIONIS Pydantic Schemas
"""
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============== ENUMS ==============

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class TenantPlan(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class RoleType(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# ============== BASE SCHEMAS ==============

class SuccessResponse(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    meta: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: Dict[str, Any]


class PaginatedResponse(BaseModel):
    success: bool = True
    data: List[Any]
    meta: Dict[str, Any] = Field(default_factory=lambda: {"page": 1, "limit": 20, "total": 0})


# ============== AUTH SCHEMAS ==============

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    two_factor_code: Optional[str] = None


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    tenant_name: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class Enable2FAResponse(BaseModel):
    secret: str
    qr_code: str


class Verify2FARequest(BaseModel):
    code: str


class OAuthSessionRequest(BaseModel):
    session_id: str


# ============== USER SCHEMAS ==============

class UserBase(BaseModel):
    email: EmailStr
    name: str
    avatar_url: Optional[str] = None
    language: str = "pt-BR"
    timezone: str = "America/Sao_Paulo"


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    status: UserStatus
    is_verified: bool
    two_factor_enabled: bool
    created_at: datetime
    updated_at: datetime


class UserWithTenant(UserResponse):
    current_tenant: Optional["TenantResponse"] = None
    role: Optional[str] = None
    permissions: List[str] = []


# ============== TENANT SCHEMAS ==============

class TenantBase(BaseModel):
    name: str
    slug: Optional[str] = None
    logo_url: Optional[str] = None
    domain: Optional[str] = None
    slogan: Optional[str] = None
    brand_primary: str = "#00e5ff"
    brand_secondary: str = "#ff9d00"
    ai_name: str = "ORIONIS"
    ai_persona: Optional[str] = None


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    logo_url: Optional[str] = None
    domain: Optional[str] = None
    slogan: Optional[str] = None
    brand_primary: Optional[str] = None
    brand_secondary: Optional[str] = None
    ai_name: Optional[str] = None
    ai_persona: Optional[str] = None


class TenantResponse(TenantBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    plan: TenantPlan
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ============== SETTINGS SCHEMAS ==============

class UserSettingsUpdate(BaseModel):
    voice_enabled: Optional[bool] = None
    voice_name: Optional[str] = None
    voice_speed: Optional[float] = None
    voice_auto_response: Optional[bool] = None
    camera_enabled: Optional[bool] = None
    ocr_enabled: Optional[bool] = None
    vision_mode: Optional[str] = None
    memory_enabled: Optional[bool] = None
    memory_retention_days: Optional[int] = None
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None


class UserSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    voice_enabled: bool
    voice_name: str
    voice_speed: float
    voice_auto_response: bool
    camera_enabled: bool
    ocr_enabled: bool
    vision_mode: str
    memory_enabled: bool
    memory_retention_days: int
    email_notifications: bool
    push_notifications: bool


class TenantSettingsUpdate(BaseModel):
    company_name: Optional[str] = None
    company_logo: Optional[str] = None
    custom_domain: Optional[str] = None
    automation_enabled: Optional[bool] = None
    knowledge_auto_index: Optional[bool] = None
    website_builder_enabled: Optional[bool] = None
    app_builder_enabled: Optional[bool] = None
    feature_flags: Optional[Dict[str, bool]] = None


class TenantSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    company_name: Optional[str]
    company_logo: Optional[str]
    custom_domain: Optional[str]
    automation_enabled: bool
    knowledge_auto_index: bool
    website_builder_enabled: bool
    app_builder_enabled: bool
    feature_flags: Dict[str, bool]


class AIModelSettingsUpdate(BaseModel):
    primary_model: Optional[str] = None
    fast_model: Optional[str] = None
    vision_model: Optional[str] = None
    voice_model: Optional[str] = None
    tts_model: Optional[str] = None
    image_model: Optional[str] = None
    temperature: Optional[float] = None
    max_context_tokens: Optional[int] = None
    response_style: Optional[str] = None


class AIModelSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    primary_model: str
    fast_model: str
    vision_model: str
    voice_model: str
    tts_model: str
    image_model: str
    temperature: float
    max_context_tokens: int
    response_style: str


class SecuritySettingsUpdate(BaseModel):
    two_factor_required: Optional[bool] = None
    session_timeout_minutes: Optional[int] = None
    allow_api_keys: Optional[bool] = None
    max_api_keys: Optional[int] = None
    audit_log_retention_days: Optional[int] = None
    ip_whitelist: Optional[List[str]] = None


class SecuritySettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    two_factor_required: bool
    session_timeout_minutes: int
    allow_api_keys: bool
    max_api_keys: int
    audit_log_retention_days: int
    ip_whitelist: List[str]


# ============== CHAT SCHEMAS ==============

class ConversationCreate(BaseModel):
    title: Optional[str] = "Nova Conversa"
    system_prompt: Optional[str] = None
    model: Optional[str] = None


class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    is_archived: Optional[bool] = None
    is_pinned: Optional[bool] = None


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    title: str
    summary: Optional[str]
    is_archived: bool
    is_pinned: bool
    model: str
    total_messages: int
    created_at: datetime
    updated_at: datetime


class MessageCreate(BaseModel):
    content: str
    content_type: str = "text"
    image_base64: Optional[str] = None


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    conversation_id: str
    role: MessageRole
    content: str
    content_type: str
    agent_name: Optional[str]
    created_at: datetime


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    image_base64: Optional[str] = None
    stream: bool = False


class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    role: str = "assistant"
    agent_name: Optional[str] = None


# ============== VOICE SCHEMAS ==============

class VoiceTranscribeResponse(BaseModel):
    text: str
    language: Optional[str] = None
    duration: Optional[float] = None


class VoiceSpeakRequest(BaseModel):
    text: str
    voice: str = "nova"
    speed: float = 1.0


class VoiceSpeakResponse(BaseModel):
    audio_base64: str


class VoiceSettingsUpdate(BaseModel):
    voice_enabled: Optional[bool] = None
    voice_name: Optional[str] = None
    voice_speed: Optional[float] = None
    voice_auto_response: Optional[bool] = None


# ============== VISION SCHEMAS ==============

class VisionAnalyzeRequest(BaseModel):
    image_base64: str
    question: str = "Descreva detalhadamente esta imagem."
    analysis_type: str = "general"  # general, ocr, document, interface


class VisionAnalyzeResponse(BaseModel):
    analysis: str
    analysis_type: str
    metadata: Optional[Dict[str, Any]] = None


# ============== IMAGE GENERATION SCHEMAS ==============

class ImageGenerateRequest(BaseModel):
    prompt: str
    size: str = "1024x1024"
    quality: str = "standard"
    n: int = 1


class ImageGenerateResponse(BaseModel):
    images: List[str]  # base64 encoded


# ============== RESEARCH SCHEMAS ==============

class ResearchRequest(BaseModel):
    query: str
    max_results: int = 5
    providers: Optional[List[str]] = None


class ResearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    source: str
    score: float


class ResearchResponse(BaseModel):
    query: str
    results: List[ResearchResult]
    summary: Optional[str] = None


# ============== KNOWLEDGE BASE SCHEMAS ==============

class KnowledgeDocumentCreate(BaseModel):
    name: str
    namespace: str = "default"


class KnowledgeDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    name: str
    file_type: str
    file_size: int
    status: str
    chunk_count: int
    namespace: str
    created_at: datetime


class KnowledgeSearchRequest(BaseModel):
    query: str
    namespace: Optional[str] = None
    limit: int = 5


class KnowledgeSearchResult(BaseModel):
    document_id: str
    document_name: str
    chunk_content: str
    score: float


# ============== MEMORY SCHEMAS ==============

class MemoryCreate(BaseModel):
    content: str
    memory_type: str = "general"
    importance: float = 0.5


class MemoryUpdate(BaseModel):
    content: Optional[str] = None
    importance: Optional[float] = None


class MemoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    content: str
    memory_type: str
    importance: float
    access_count: int
    created_at: datetime


class MemoryQueryRequest(BaseModel):
    query: str
    limit: int = 10
    memory_type: Optional[str] = None


# ============== INTEGRATION SCHEMAS ==============

class IntegrationConnectRequest(BaseModel):
    credentials: Dict[str, Any]
    config: Optional[Dict[str, Any]] = None


class IntegrationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    provider: str
    name: str
    status: str
    last_sync_at: Optional[datetime]
    created_at: datetime


# ============== AUTOMATION SCHEMAS ==============

class AutomationCreate(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_type: str
    trigger_config: Dict[str, Any]
    actions: List[Dict[str, Any]]


class AutomationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    trigger_config: Optional[Dict[str, Any]] = None
    actions: Optional[List[Dict[str, Any]]] = None


class AutomationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    name: str
    description: Optional[str]
    status: str
    trigger_type: str
    trigger_config: Dict[str, Any]
    actions: List[Dict[str, Any]]
    run_count: int
    last_run_at: Optional[datetime]
    created_at: datetime


# ============== AGENT SCHEMAS ==============

class AgentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    name: str
    display_name: str
    description: Optional[str]
    agent_type: str
    status: str
    capabilities: List[str]


class AgentRunRequest(BaseModel):
    agent_name: str
    input_data: Dict[str, Any]


class AgentRunResponse(BaseModel):
    id: str
    agent_name: str
    status: str
    output_data: Dict[str, Any]
    duration_ms: int


# ============== ANALYTICS SCHEMAS ==============

class AnalyticsOverview(BaseModel):
    total_conversations: int
    total_messages: int
    total_tokens: int
    total_voice_minutes: float
    total_images: int
    active_users: int
    period: str


class UsageStats(BaseModel):
    chat_messages: int
    tokens_used: int
    voice_minutes: float
    images_generated: int
    documents_indexed: int
    api_calls: int
    total_cost: float


# ============== BILLING SCHEMAS ==============

class BillingPlanResponse(BaseModel):
    current_plan: TenantPlan
    credit_balance: float
    usage_limit: int
    features: Dict[str, bool]


class BillingUsageResponse(BaseModel):
    period_start: datetime
    period_end: datetime
    usage: UsageStats
    remaining_credits: float


# ============== AUDIT LOG SCHEMAS ==============

class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: Optional[str]
    action: str
    resource_type: str
    resource_id: Optional[str]
    ip_address: Optional[str]
    created_at: datetime


# ============== SYSTEM SCHEMAS ==============

class SystemStatusResponse(BaseModel):
    system: str
    version: str
    status: str
    uptime: str
    agents: List[AgentResponse]
    capabilities: Dict[str, bool]


class HealthResponse(BaseModel):
    status: str
    database: str
    redis: str
    version: str
