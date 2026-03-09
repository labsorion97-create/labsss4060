"""
ORIONIS Agent Service
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import Agent, AgentRun, AgentStatus
from app.schemas.schemas import AgentResponse, AgentRunResponse


# Default agents configuration
DEFAULT_AGENTS = [
    {
        "name": "core_orchestrator",
        "display_name": "Core Orchestrator",
        "description": "Núcleo central que orquestra todos os agentes",
        "agent_type": "core",
        "status": AgentStatus.ACTIVE,
        "capabilities": ["routing", "planning", "coordination"]
    },
    {
        "name": "planner",
        "display_name": "Planner Agent",
        "description": "Interpreta intenções e cria planos de execução",
        "agent_type": "core",
        "status": AgentStatus.ACTIVE,
        "capabilities": ["planning", "task_decomposition"]
    },
    {
        "name": "research",
        "display_name": "Research Agent",
        "description": "Pesquisa informações em tempo real",
        "agent_type": "knowledge",
        "status": AgentStatus.ACTIVE,
        "capabilities": ["web_search", "data_analysis", "fact_checking"]
    },
    {
        "name": "knowledge",
        "display_name": "Knowledge Agent",
        "description": "Consulta base de conhecimento interna",
        "agent_type": "knowledge",
        "status": AgentStatus.ACTIVE,
        "capabilities": ["rag", "document_search", "semantic_search"]
    },
    {
        "name": "memory",
        "display_name": "Memory Agent",
        "description": "Gerencia memória de curto e longo prazo",
        "agent_type": "knowledge",
        "status": AgentStatus.ACTIVE,
        "capabilities": ["memory_storage", "context_retrieval"]
    },
    {
        "name": "voice",
        "display_name": "Voice Agent",
        "description": "Transcrição e síntese de voz",
        "agent_type": "multimodal",
        "status": AgentStatus.ACTIVE,
        "capabilities": ["stt", "tts", "voice_commands"]
    },
    {
        "name": "vision",
        "display_name": "Vision Agent",
        "description": "Análise de imagens e visão computacional",
        "agent_type": "multimodal",
        "status": AgentStatus.ACTIVE,
        "capabilities": ["image_analysis", "ocr", "object_detection"]
    },
    {
        "name": "design",
        "display_name": "Design Agent",
        "description": "Geração de imagens e design visual",
        "agent_type": "builder",
        "status": AgentStatus.ACTIVE,
        "capabilities": ["image_generation", "logo_creation", "visual_design"]
    },
    {
        "name": "development",
        "display_name": "Development Agent",
        "description": "Geração de código e desenvolvimento",
        "agent_type": "builder",
        "status": AgentStatus.STANDBY,
        "capabilities": ["code_generation", "debugging", "refactoring"]
    },
    {
        "name": "website_builder",
        "display_name": "Website Builder Agent",
        "description": "Criação de sites e landing pages",
        "agent_type": "builder",
        "status": AgentStatus.STANDBY,
        "capabilities": ["site_generation", "copy_writing", "seo"]
    },
    {
        "name": "app_builder",
        "display_name": "App Builder Agent",
        "description": "Criação de aplicações e dashboards",
        "agent_type": "builder",
        "status": AgentStatus.STANDBY,
        "capabilities": ["app_generation", "ui_design", "api_creation"]
    },
    {
        "name": "sales",
        "display_name": "Sales Agent",
        "description": "Prospecção e automação de vendas",
        "agent_type": "operational",
        "status": AgentStatus.STANDBY,
        "capabilities": ["lead_qualification", "scripts", "follow_ups"]
    },
    {
        "name": "operations",
        "display_name": "Operations Agent",
        "description": "Tarefas operacionais e SOPs",
        "agent_type": "operational",
        "status": AgentStatus.STANDBY,
        "capabilities": ["sop_creation", "task_coordination", "reporting"]
    },
    {
        "name": "automation",
        "display_name": "Automation Agent",
        "description": "Criação e execução de workflows",
        "agent_type": "operational",
        "status": AgentStatus.ACTIVE,
        "capabilities": ["workflow_creation", "triggers", "scheduling"]
    },
    {
        "name": "integration",
        "display_name": "Integration Agent",
        "description": "Conexão com APIs externas",
        "agent_type": "operational",
        "status": AgentStatus.ACTIVE,
        "capabilities": ["api_connection", "webhooks", "data_sync"]
    },
    {
        "name": "analytics",
        "display_name": "Analytics Agent",
        "description": "Análise de métricas e performance",
        "agent_type": "operational",
        "status": AgentStatus.ACTIVE,
        "capabilities": ["metrics_analysis", "reporting", "insights"]
    },
    {
        "name": "supervisor",
        "display_name": "Supervisor Agent",
        "description": "Valida qualidade das respostas",
        "agent_type": "core",
        "status": AgentStatus.ACTIVE,
        "capabilities": ["quality_check", "coherence_validation"]
    },
    {
        "name": "security",
        "display_name": "Security Agent",
        "description": "Auditoria e controle de acesso",
        "agent_type": "core",
        "status": AgentStatus.ACTIVE,
        "capabilities": ["rbac", "audit", "threat_detection"]
    }
]


class AgentService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def initialize_agents(self):
        """Initialize default agents in database"""
        for agent_config in DEFAULT_AGENTS:
            result = await self.db.execute(
                select(Agent).where(Agent.name == agent_config["name"])
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                agent = Agent(**agent_config)
                self.db.add(agent)
        
        await self.db.commit()
    
    async def get_all_agents(self) -> List[AgentResponse]:
        """Get all agents"""
        result = await self.db.execute(select(Agent))
        agents = result.scalars().all()
        
        if not agents:
            await self.initialize_agents()
            result = await self.db.execute(select(Agent))
            agents = result.scalars().all()
        
        return [AgentResponse.model_validate(a) for a in agents]
    
    async def get_agent(self, name: str) -> Optional[AgentResponse]:
        """Get agent by name"""
        result = await self.db.execute(select(Agent).where(Agent.name == name))
        agent = result.scalar_one_or_none()
        
        if agent:
            return AgentResponse.model_validate(agent)
        return None
    
    async def get_agents_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        agents = await self.get_all_agents()
        
        active = len([a for a in agents if a.status == "active"])
        standby = len([a for a in agents if a.status == "standby"])
        disabled = len([a for a in agents if a.status == "disabled"])
        
        return {
            "total": len(agents),
            "active": active,
            "standby": standby,
            "disabled": disabled,
            "agents": agents
        }
    
    async def run_agent(
        self,
        agent_name: str,
        tenant_id: str,
        user_id: Optional[str],
        input_data: Dict[str, Any]
    ) -> AgentRunResponse:
        """Execute an agent task"""
        result = await self.db.execute(select(Agent).where(Agent.name == agent_name))
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise ValueError(f"Agent {agent_name} not found")
        
        if agent.status != AgentStatus.ACTIVE:
            raise ValueError(f"Agent {agent_name} is not active")
        
        # Create run record
        start_time = datetime.now(timezone.utc)
        
        run = AgentRun(
            agent_id=agent.id,
            tenant_id=tenant_id,
            user_id=user_id,
            input_data=input_data,
            status="running"
        )
        self.db.add(run)
        await self.db.flush()
        
        # Execute agent logic (simplified)
        try:
            output_data = await self._execute_agent(agent_name, input_data)
            run.status = "success"
            run.output_data = output_data
        except Exception as e:
            run.status = "failed"
            run.output_data = {"error": str(e)}
        
        end_time = datetime.now(timezone.utc)
        run.completed_at = end_time
        run.duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        await self.db.commit()
        
        return AgentRunResponse(
            id=run.id,
            agent_name=agent_name,
            status=run.status,
            output_data=run.output_data,
            duration_ms=run.duration_ms
        )
    
    async def _execute_agent(self, agent_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent-specific logic"""
        # This would dispatch to specific agent implementations
        # For now, return a placeholder response
        return {
            "agent": agent_name,
            "status": "completed",
            "result": f"Agent {agent_name} processed input successfully"
        }
