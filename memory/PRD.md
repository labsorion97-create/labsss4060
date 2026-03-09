# ORIONIS - PRD (Product Requirements Document)

## Visão Geral
**Nome:** ORIONIS - Orion Intelligent System  
**Versão:** 3.0  
**Data:** Janeiro 2026  

## Problema Statement Original
Sistema operacional de inteligência artificial universal no estilo Jarvis + Apple + NVIDIA. Um núcleo de inteligência capaz de pensar, pesquisar, criar, construir, automatizar e operar como um sistema completo de IA.

## User Personas
1. **Profissional de Tecnologia:** Precisa de assistência IA para desenvolvimento, análise e automação
2. **Empreendedor:** Busca ferramentas de pesquisa, planejamento e criação de conteúdo
3. **Criativo:** Necessita de geração de imagens e assistência criativa

## Core Requirements (Estático)
- Interface neural holográfica estilo Jarvis
- Chat IA com memória persistente (GPT-4o)
- Comando por voz (STT/TTS)
- Análise de imagens e câmera (Vision)
- Geração de imagens IA (gpt-image-1)
- Autenticação Google OAuth (Emergent Auth)
- Multi-agente virtual (9 agentes)

## Implementado ✅
- [x] **Landing Page Neural** - ORB central com anéis orbitais, partículas, scanner arc
- [x] **Sistema de Autenticação** - Google OAuth via Emergent Auth
- [x] **Dashboard Completo** - Sidebar, chat area, painéis de status
- [x] **Chat IA Inteligente** - GPT-4o com memória de conversação
- [x] **Voice Agent** - Transcrição (Whisper) + Síntese (TTS)
- [x] **Vision Agent** - Análise de imagens com GPT-4o Vision
- [x] **Design Agent** - Geração de imagens com gpt-image-1
- [x] **Histórico de Conversas** - CRUD completo no MongoDB
- [x] **Interface Responsiva** - Desktop, tablet, mobile
- [x] **Animações CSS** - Scanlines, hex grid, pulsos, rotações

## Arquitetura Técnica
```
Frontend: React 19 + Tailwind CSS
Backend: FastAPI + Python
Database: MongoDB
Auth: Emergent Google OAuth
AI: OpenAI GPT-4o, Whisper, TTS, gpt-image-1
Key: Emergent LLM Key (Universal)
```

## APIs Implementadas
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| /api/auth/session | POST | Exchange OAuth session |
| /api/auth/me | GET | Get current user |
| /api/auth/logout | POST | Logout user |
| /api/chat | POST | Send chat message |
| /api/conversations | GET | List conversations |
| /api/conversations/{id}/messages | GET | Get messages |
| /api/voice/transcribe | POST | Audio to text |
| /api/voice/speak | POST | Text to audio |
| /api/vision/analyze | POST | Analyze image |
| /api/image/generate | POST | Generate image |
| /api/system/status | GET | System status |

## Backlog Priorizado

### P0 (Crítico)
- [x] Chat funcional
- [x] Autenticação
- [x] Voice básico

### P1 (Importante)
- [ ] Streaming de respostas (SSE)
- [ ] Pesquisa web em tempo real
- [ ] RAG com documentos

### P2 (Desejável)
- [ ] Multi-tenant / White-label
- [ ] Mais agentes especializados
- [ ] Dashboard de analytics
- [ ] Integração WhatsApp/Telegram

## Próximos Passos
1. Implementar streaming de chat para respostas em tempo real
2. Adicionar Research Agent com pesquisa web
3. Sistema de memória de longo prazo (Knowledge Base)
4. Dashboard de métricas e custos

## Métricas de Sucesso
- 100% de testes passados
- < 2s tempo de resposta do chat
- Interface responsiva em todos dispositivos
- 0 erros de console JavaScript
