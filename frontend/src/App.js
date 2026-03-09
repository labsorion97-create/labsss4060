import { useState, useEffect, useRef, useCallback, createContext, useContext } from "react";
import { BrowserRouter, Routes, Route, useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import "@/App.css";
import { Toaster } from "@/components/ui/sonner";
import { toast } from "sonner";
import { 
  Mic, MicOff, Camera, Send, Volume2, VolumeX, Image, 
  MessageSquare, Settings, LogOut, Trash2, Plus, X,
  Zap, Brain, Eye, Sparkles, Activity, Cpu, Loader2,
  MoreVertical, Globe, Key, Search, ImageIcon, Video,
  Users, Database, Shield, RefreshCw, BarChart3, Bot,
  Cog, ChevronRight, Check, Play, Pause, Volume1,
  FileText, Code, Layout, Layers, Radio, Wifi, Power,
  Terminal, Server, HardDrive, Monitor, Headphones,
  Languages, Palette, Moon, Sun, Bell, Lock, Save, 
  Upload, Download, History, Bookmark, Star, Crown
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// ============== SYSTEM STATE CONTEXT ==============
const SystemStateContext = createContext();

const useSystemState = () => useContext(SystemStateContext);

const SystemStateProvider = ({ children }) => {
  const [systemState, setSystemState] = useState('idle');
  const [activeAgents, setActiveAgents] = useState([]);
  const [isMultiAgent, setIsMultiAgent] = useState(false);
  
  const updateState = (newState) => setSystemState(newState);
  const setAgents = (agents) => {
    setActiveAgents(agents);
    setIsMultiAgent(agents.length > 1);
  };
  
  return (
    <SystemStateContext.Provider value={{ 
      systemState, updateState, activeAgents, setAgents, isMultiAgent 
    }}>
      {children}
    </SystemStateContext.Provider>
  );
};

// ============== AUTH CONTEXT ==============
const AuthContext = ({ children }) => {
  const location = useLocation();
  if (location.hash?.includes('session_id=')) {
    return <AuthCallback />;
  }
  return children;
};

// ============== AUTH CALLBACK ==============
const AuthCallback = () => {
  const navigate = useNavigate();
  const hasProcessed = useRef(false);
  
  useEffect(() => {
    if (hasProcessed.current) return;
    hasProcessed.current = true;
    
    const processAuth = async () => {
      const hash = window.location.hash;
      const sessionId = hash.split('session_id=')[1]?.split('&')[0];
      
      if (!sessionId) {
        navigate('/');
        return;
      }
      
      try {
        const response = await axios.post(`${API}/auth/session`, {
          session_id: sessionId
        }, { withCredentials: true });
        
        window.history.replaceState(null, '', window.location.pathname);
        navigate('/dashboard', { state: { user: response.data } });
      } catch (error) {
        console.error('Auth error:', error);
        toast.error('Falha na autenticação');
        navigate('/');
      }
    };
    
    processAuth();
  }, [navigate]);
  
  return (
    <div className="min-h-screen bg-[#000a14] flex items-center justify-center">
      <div className="text-center">
        <NeuralOrb3D state="thinking" size="large" />
        <p className="text-cyan-400 mt-4 font-mono">Autenticando...</p>
      </div>
    </div>
  );
};

// ============== NEURAL ORB 3D COMPONENT ==============
const NeuralOrb3D = ({ state = 'idle', size = 'medium', activeAgents = [] }) => {
  const sizeClasses = {
    small: 'w-20 h-20',
    medium: 'w-32 h-32',
    large: 'w-48 h-48',
    xlarge: 'w-64 h-64'
  };
  
  const stateConfig = {
    idle: { color: 'cyan', intensity: 1, pulse: 'slow', particles: 3 },
    listening: { color: 'green', intensity: 1.5, pulse: 'medium', particles: 5 },
    thinking: { color: 'amber', intensity: 2, pulse: 'fast', particles: 8 },
    researching: { color: 'purple', intensity: 1.8, pulse: 'medium', particles: 6 },
    creating: { color: 'pink', intensity: 2.2, pulse: 'fast', particles: 10 },
    speaking: { color: 'blue', intensity: 1.6, pulse: 'wave', particles: 4 },
    executing: { color: 'orange', intensity: 2.5, pulse: 'fast', particles: 12 },
    'multi-agent': { color: 'rainbow', intensity: 3, pulse: 'ultra', particles: 15 }
  };
  
  const config = stateConfig[state] || stateConfig.idle;
  const isMultiAgent = state === 'multi-agent' || activeAgents.length > 1;
  
  return (
    <div className={`neural-orb-3d ${sizeClasses[size]} ${state}`} data-state={state}>
      {/* Core Brain */}
      <div className={`orb-core-3d ${config.color}`}>
        <Brain className="w-1/2 h-1/2 text-current" />
        <div className="core-glow" />
        <div className="core-pulse" style={{ animationDuration: config.pulse === 'fast' ? '0.5s' : config.pulse === 'medium' ? '1s' : '2s' }} />
      </div>
      
      {/* Neural Rings */}
      <div className="neural-ring ring-1" style={{ '--ring-speed': '20s' }}>
        {[...Array(config.particles)].map((_, i) => (
          <div key={i} className="neural-particle" style={{ '--delay': `${i * 0.5}s`, '--angle': `${i * (360 / config.particles)}deg` }} />
        ))}
      </div>
      <div className="neural-ring ring-2" style={{ '--ring-speed': '30s' }}>
        {[...Array(Math.ceil(config.particles / 2))].map((_, i) => (
          <div key={i} className="neural-particle" style={{ '--delay': `${i * 0.7}s`, '--angle': `${i * (360 / (config.particles / 2))}deg` }} />
        ))}
      </div>
      <div className="neural-ring ring-3" style={{ '--ring-speed': '40s' }}>
        {[...Array(Math.ceil(config.particles / 3))].map((_, i) => (
          <div key={i} className="neural-particle" style={{ '--delay': `${i * 1}s`, '--angle': `${i * (360 / (config.particles / 3))}deg` }} />
        ))}
      </div>
      
      {/* Scanner Arc */}
      <div className="scanner-arc-3d" />
      
      {/* Synaptic Connections */}
      <div className="synaptic-layer">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="synapse-line" style={{ '--angle': `${i * 60}deg` }} />
        ))}
      </div>
      
      {/* Agent Orbiters (when multi-agent) */}
      {isMultiAgent && activeAgents.slice(0, 5).map((agent, i) => (
        <div 
          key={agent.name || i} 
          className="agent-orbiter" 
          style={{ '--orbit-angle': `${i * 72}deg`, '--orbit-delay': `${i * 0.2}s` }}
          title={agent.display_name || agent.name}
        >
          <Bot className="w-4 h-4" />
        </div>
      ))}
      
      {/* Sound Waves (when speaking) */}
      {state === 'speaking' && (
        <div className="sound-waves">
          <div className="wave wave-1" />
          <div className="wave wave-2" />
          <div className="wave wave-3" />
        </div>
      )}
      
      {/* Data Streams (when researching) */}
      {state === 'researching' && (
        <div className="data-streams-orb">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="data-stream" style={{ '--stream-angle': `${i * 90}deg` }} />
          ))}
        </div>
      )}
    </div>
  );
};

// ============== SETTINGS PANEL ==============
const SettingsPanel = ({ isOpen, onClose, user }) => {
  const [activeTab, setActiveTab] = useState('general');
  const [settings, setSettings] = useState({
    general: {
      language: 'pt-BR',
      theme: 'dark',
      aiName: 'ORIONIS',
      operationMode: 'balanced',
      autoSave: true
    },
    api: {
      emergentKey: '',
      customApis: [],
      logsEnabled: true
    },
    voice: {
      enabled: true,
      autoSpeak: false,
      voiceName: 'nova',
      speed: 1.0,
      volume: 0.8,
      language: 'pt-BR',
      pushToTalk: false
    },
    research: {
      enabled: true,
      depth: 'balanced',
      engines: ['google', 'bing'],
      cacheEnabled: true,
      maxResults: 10
    },
    image: {
      enabled: true,
      defaultStyle: 'realistic',
      quality: 'standard',
      size: '1024x1024',
      provider: 'openai'
    },
    vision: {
      enabled: true,
      ocrEnabled: true,
      realTimeAnalysis: false,
      mode: 'general'
    },
    str: {
      enabled: true,
      mode: 'auto',
      fallbackEnabled: true,
      logLevel: 'info',
      timeout: 30
    },
    agents: {
      simultaneousEnabled: true,
      maxConcurrent: 5,
      autoSelect: true,
      priorityMode: 'smart'
    },
    leader: {
      enabled: true,
      autonomyLevel: 'high',
      consolidationMode: 'smart',
      fallbackPolicy: 'retry'
    },
    memory: {
      enabled: true,
      retentionDays: 90,
      personalMemory: true,
      projectMemory: true
    },
    knowledge: {
      autoIndex: true,
      namespaces: ['default'],
      reprocessOnUpdate: true
    },
    automation: {
      enabled: true,
      maxTriggers: 10,
      loggingEnabled: true
    },
    builders: {
      siteBuilderEnabled: true,
      appBuilderEnabled: true,
      autoPreview: true,
      templates: ['modern', 'minimal', 'premium']
    },
    security: {
      twoFactorEnabled: false,
      sessionTimeout: 480,
      apiKeysAllowed: true,
      auditLogging: true
    },
    updates: {
      autoUpdates: true,
      channel: 'stable',
      rollbackEnabled: true
    },
    analytics: {
      enabled: true,
      trackUsage: true,
      trackCosts: true,
      trackPerformance: true
    }
  });
  
  const [isSaving, setIsSaving] = useState(false);
  
  const saveSettings = async () => {
    setIsSaving(true);
    try {
      await axios.put(`${API}/v1/settings/profile`, settings.general, { withCredentials: true });
      toast.success('Configurações salvas');
    } catch (error) {
      toast.error('Erro ao salvar configurações');
    } finally {
      setIsSaving(false);
    }
  };
  
  const testVoice = async () => {
    try {
      const response = await axios.post(`${API}/voice/speak`, {
        text: 'Teste de voz da ORIONIS. Sistema operacional de inteligência artificial.',
        voice: settings.voice.voiceName
      }, { withCredentials: true });
      
      const audio = new Audio(`data:audio/mp3;base64,${response.data.audio_base64}`);
      audio.volume = settings.voice.volume;
      audio.playbackRate = settings.voice.speed;
      audio.play();
      toast.success('Teste de voz executado');
    } catch (error) {
      toast.error('Erro no teste de voz');
    }
  };
  
  const testApi = async () => {
    try {
      const response = await axios.get(`${API}/health`, { withCredentials: true });
      if (response.data.status === 'online') {
        toast.success('API conectada com sucesso');
      }
    } catch (error) {
      toast.error('Erro ao testar API');
    }
  };
  
  if (!isOpen) return null;
  
  const tabs = [
    { id: 'general', label: 'Geral', icon: Cog },
    { id: 'api', label: 'API', icon: Key },
    { id: 'voice', label: 'Voz', icon: Volume2 },
    { id: 'research', label: 'Pesquisa', icon: Search },
    { id: 'image', label: 'Imagem', icon: ImageIcon },
    { id: 'vision', label: 'Câmera/Visão', icon: Eye },
    { id: 'str', label: 'STR', icon: Terminal },
    { id: 'agents', label: 'Agentes', icon: Users },
    { id: 'leader', label: 'Agente Líder', icon: Crown },
    { id: 'memory', label: 'Memória', icon: Database },
    { id: 'knowledge', label: 'Conhecimento', icon: FileText },
    { id: 'automation', label: 'Automação', icon: Zap },
    { id: 'builders', label: 'Sites/Apps', icon: Layout },
    { id: 'security', label: 'Segurança', icon: Shield },
    { id: 'updates', label: 'Atualizações', icon: RefreshCw },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 }
  ];
  
  return (
    <div className="settings-overlay" data-testid="settings-panel">
      <div className="settings-panel">
        {/* Header */}
        <div className="settings-header">
          <div className="settings-title">
            <Settings className="w-5 h-5" />
            <span>Configurações da ORIONIS</span>
          </div>
          <div className="settings-actions">
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={saveSettings}
              disabled={isSaving}
              className="save-btn"
            >
              {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
              Salvar
            </Button>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>
        
        {/* Content */}
        <div className="settings-content">
          {/* Tabs Sidebar */}
          <div className="settings-tabs-sidebar">
            <ScrollArea className="h-full">
              {tabs.map(tab => (
                <button
                  key={tab.id}
                  className={`settings-tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                  onClick={() => setActiveTab(tab.id)}
                >
                  <tab.icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                  <ChevronRight className="w-4 h-4 chevron" />
                </button>
              ))}
            </ScrollArea>
          </div>
          
          {/* Tab Content */}
          <div className="settings-tab-content">
            <ScrollArea className="h-full">
              {/* GENERAL */}
              {activeTab === 'general' && (
                <div className="settings-section">
                  <h3>Configurações Gerais</h3>
                  
                  <div className="setting-group">
                    <Label>Nome da IA</Label>
                    <Input 
                      value={settings.general.aiName}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        general: { ...prev.general, aiName: e.target.value }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-group">
                    <Label>Idioma</Label>
                    <Select 
                      value={settings.general.language}
                      onValueChange={(v) => setSettings(prev => ({
                        ...prev,
                        general: { ...prev.general, language: v }
                      }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="pt-BR">Português (Brasil)</SelectItem>
                        <SelectItem value="en-US">English (US)</SelectItem>
                        <SelectItem value="es-ES">Español</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="setting-group">
                    <Label>Tema</Label>
                    <Select 
                      value={settings.general.theme}
                      onValueChange={(v) => setSettings(prev => ({
                        ...prev,
                        general: { ...prev.general, theme: v }
                      }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="dark">Escuro (Jarvis)</SelectItem>
                        <SelectItem value="light">Claro</SelectItem>
                        <SelectItem value="system">Sistema</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="setting-group">
                    <Label>Modo de Operação</Label>
                    <Select 
                      value={settings.general.operationMode}
                      onValueChange={(v) => setSettings(prev => ({
                        ...prev,
                        general: { ...prev.general, operationMode: v }
                      }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="fast">Rápido</SelectItem>
                        <SelectItem value="balanced">Balanceado</SelectItem>
                        <SelectItem value="precise">Preciso</SelectItem>
                        <SelectItem value="creative">Criativo</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Salvamento Automático</Label>
                      <span className="setting-desc">Salvar configurações automaticamente</span>
                    </div>
                    <Switch 
                      checked={settings.general.autoSave}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        general: { ...prev.general, autoSave: v }
                      }))}
                    />
                  </div>
                </div>
              )}
              
              {/* API */}
              {activeTab === 'api' && (
                <div className="settings-section">
                  <h3>Configurações de API</h3>
                  
                  <div className="setting-group">
                    <Label>Chave Emergent LLM</Label>
                    <Input 
                      type="password"
                      value={settings.api.emergentKey}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        api: { ...prev.api, emergentKey: e.target.value }
                      }))}
                      placeholder="sk-emergent-..."
                    />
                  </div>
                  
                  <div className="setting-group">
                    <Label>APIs Customizadas</Label>
                    <div className="api-list">
                      {settings.api.customApis.length === 0 && (
                        <p className="text-muted">Nenhuma API customizada configurada</p>
                      )}
                    </div>
                    <Button variant="outline" size="sm" className="mt-2">
                      <Plus className="w-4 h-4 mr-2" />
                      Adicionar API
                    </Button>
                  </div>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Logs de API</Label>
                      <span className="setting-desc">Registrar chamadas de API</span>
                    </div>
                    <Switch 
                      checked={settings.api.logsEnabled}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        api: { ...prev.api, logsEnabled: v }
                      }))}
                    />
                  </div>
                  
                  <Button onClick={testApi} className="test-btn">
                    <Wifi className="w-4 h-4 mr-2" />
                    Testar Conexão
                  </Button>
                </div>
              )}
              
              {/* VOICE */}
              {activeTab === 'voice' && (
                <div className="settings-section">
                  <h3>Configurações de Voz</h3>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Voz Ativada</Label>
                      <span className="setting-desc">Habilitar síntese de voz</span>
                    </div>
                    <Switch 
                      checked={settings.voice.enabled}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        voice: { ...prev.voice, enabled: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Resposta Automática por Voz</Label>
                      <span className="setting-desc">ORIONIS fala automaticamente</span>
                    </div>
                    <Switch 
                      checked={settings.voice.autoSpeak}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        voice: { ...prev.voice, autoSpeak: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-group">
                    <Label>Voz</Label>
                    <Select 
                      value={settings.voice.voiceName}
                      onValueChange={(v) => setSettings(prev => ({
                        ...prev,
                        voice: { ...prev.voice, voiceName: v }
                      }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="alloy">Alloy</SelectItem>
                        <SelectItem value="echo">Echo</SelectItem>
                        <SelectItem value="fable">Fable</SelectItem>
                        <SelectItem value="nova">Nova</SelectItem>
                        <SelectItem value="onyx">Onyx</SelectItem>
                        <SelectItem value="shimmer">Shimmer</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="setting-group">
                    <Label>Velocidade: {settings.voice.speed}x</Label>
                    <Slider 
                      value={[settings.voice.speed]}
                      min={0.5}
                      max={2}
                      step={0.1}
                      onValueChange={([v]) => setSettings(prev => ({
                        ...prev,
                        voice: { ...prev.voice, speed: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-group">
                    <Label>Volume: {Math.round(settings.voice.volume * 100)}%</Label>
                    <Slider 
                      value={[settings.voice.volume]}
                      min={0}
                      max={1}
                      step={0.1}
                      onValueChange={([v]) => setSettings(prev => ({
                        ...prev,
                        voice: { ...prev.voice, volume: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Push-to-Talk</Label>
                      <span className="setting-desc">Pressionar para falar</span>
                    </div>
                    <Switch 
                      checked={settings.voice.pushToTalk}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        voice: { ...prev.voice, pushToTalk: v }
                      }))}
                    />
                  </div>
                  
                  <Button onClick={testVoice} className="test-btn">
                    <Volume2 className="w-4 h-4 mr-2" />
                    Testar Voz
                  </Button>
                </div>
              )}
              
              {/* RESEARCH */}
              {activeTab === 'research' && (
                <div className="settings-section">
                  <h3>Configurações de Pesquisa</h3>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Pesquisa Web Ativada</Label>
                      <span className="setting-desc">Buscar informações online</span>
                    </div>
                    <Switch 
                      checked={settings.research.enabled}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        research: { ...prev.research, enabled: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-group">
                    <Label>Profundidade da Busca</Label>
                    <Select 
                      value={settings.research.depth}
                      onValueChange={(v) => setSettings(prev => ({
                        ...prev,
                        research: { ...prev.research, depth: v }
                      }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="quick">Rápida</SelectItem>
                        <SelectItem value="balanced">Balanceada</SelectItem>
                        <SelectItem value="deep">Profunda</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="setting-group">
                    <Label>Máximo de Resultados: {settings.research.maxResults}</Label>
                    <Slider 
                      value={[settings.research.maxResults]}
                      min={5}
                      max={30}
                      step={5}
                      onValueChange={([v]) => setSettings(prev => ({
                        ...prev,
                        research: { ...prev.research, maxResults: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Cache de Pesquisa</Label>
                      <span className="setting-desc">Armazenar resultados recentes</span>
                    </div>
                    <Switch 
                      checked={settings.research.cacheEnabled}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        research: { ...prev.research, cacheEnabled: v }
                      }))}
                    />
                  </div>
                </div>
              )}
              
              {/* IMAGE */}
              {activeTab === 'image' && (
                <div className="settings-section">
                  <h3>Geração de Imagem</h3>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Geração Ativada</Label>
                      <span className="setting-desc">Criar imagens com IA</span>
                    </div>
                    <Switch 
                      checked={settings.image.enabled}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        image: { ...prev.image, enabled: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-group">
                    <Label>Estilo Padrão</Label>
                    <Select 
                      value={settings.image.defaultStyle}
                      onValueChange={(v) => setSettings(prev => ({
                        ...prev,
                        image: { ...prev.image, defaultStyle: v }
                      }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="realistic">Realista</SelectItem>
                        <SelectItem value="artistic">Artístico</SelectItem>
                        <SelectItem value="cinematic">Cinematográfico</SelectItem>
                        <SelectItem value="minimal">Minimalista</SelectItem>
                        <SelectItem value="futuristic">Futurista</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="setting-group">
                    <Label>Qualidade</Label>
                    <Select 
                      value={settings.image.quality}
                      onValueChange={(v) => setSettings(prev => ({
                        ...prev,
                        image: { ...prev.image, quality: v }
                      }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="standard">Standard</SelectItem>
                        <SelectItem value="hd">HD</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="setting-group">
                    <Label>Tamanho</Label>
                    <Select 
                      value={settings.image.size}
                      onValueChange={(v) => setSettings(prev => ({
                        ...prev,
                        image: { ...prev.image, size: v }
                      }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="256x256">256x256</SelectItem>
                        <SelectItem value="512x512">512x512</SelectItem>
                        <SelectItem value="1024x1024">1024x1024</SelectItem>
                        <SelectItem value="1792x1024">1792x1024</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              )}
              
              {/* VISION */}
              {activeTab === 'vision' && (
                <div className="settings-section">
                  <h3>Câmera e Visão</h3>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Câmera Ativada</Label>
                      <span className="setting-desc">Análise de imagens por câmera</span>
                    </div>
                    <Switch 
                      checked={settings.vision.enabled}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        vision: { ...prev.vision, enabled: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>OCR Ativado</Label>
                      <span className="setting-desc">Extrair texto de imagens</span>
                    </div>
                    <Switch 
                      checked={settings.vision.ocrEnabled}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        vision: { ...prev.vision, ocrEnabled: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Análise em Tempo Real</Label>
                      <span className="setting-desc">Processar frames continuamente</span>
                    </div>
                    <Switch 
                      checked={settings.vision.realTimeAnalysis}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        vision: { ...prev.vision, realTimeAnalysis: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-group">
                    <Label>Modo de Análise</Label>
                    <Select 
                      value={settings.vision.mode}
                      onValueChange={(v) => setSettings(prev => ({
                        ...prev,
                        vision: { ...prev.vision, mode: v }
                      }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="general">Geral</SelectItem>
                        <SelectItem value="document">Documento</SelectItem>
                        <SelectItem value="scene">Cena</SelectItem>
                        <SelectItem value="interface">Interface</SelectItem>
                        <SelectItem value="chart">Gráfico</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              )}
              
              {/* STR */}
              {activeTab === 'str' && (
                <div className="settings-section">
                  <h3>Configurações STR</h3>
                  <p className="section-desc">Sistema de Transcrição e Resposta em tempo real</p>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>STR Ativado</Label>
                      <span className="setting-desc">Sistema de transcrição ativo</span>
                    </div>
                    <Switch 
                      checked={settings.str.enabled}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        str: { ...prev.str, enabled: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-group">
                    <Label>Modo de Operação</Label>
                    <Select 
                      value={settings.str.mode}
                      onValueChange={(v) => setSettings(prev => ({
                        ...prev,
                        str: { ...prev.str, mode: v }
                      }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="auto">Automático</SelectItem>
                        <SelectItem value="manual">Manual</SelectItem>
                        <SelectItem value="hybrid">Híbrido</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="setting-group">
                    <Label>Timeout (segundos): {settings.str.timeout}s</Label>
                    <Slider 
                      value={[settings.str.timeout]}
                      min={10}
                      max={120}
                      step={5}
                      onValueChange={([v]) => setSettings(prev => ({
                        ...prev,
                        str: { ...prev.str, timeout: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Fallback Ativado</Label>
                      <span className="setting-desc">Usar fallback em caso de falha</span>
                    </div>
                    <Switch 
                      checked={settings.str.fallbackEnabled}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        str: { ...prev.str, fallbackEnabled: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-group">
                    <Label>Nível de Log</Label>
                    <Select 
                      value={settings.str.logLevel}
                      onValueChange={(v) => setSettings(prev => ({
                        ...prev,
                        str: { ...prev.str, logLevel: v }
                      }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="debug">Debug</SelectItem>
                        <SelectItem value="info">Info</SelectItem>
                        <SelectItem value="warn">Warn</SelectItem>
                        <SelectItem value="error">Error</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              )}
              
              {/* AGENTS */}
              {activeTab === 'agents' && (
                <div className="settings-section">
                  <h3>Sistema de Agentes</h3>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Agentes Simultâneos</Label>
                      <span className="setting-desc">Executar múltiplos agentes ao mesmo tempo</span>
                    </div>
                    <Switch 
                      checked={settings.agents.simultaneousEnabled}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        agents: { ...prev.agents, simultaneousEnabled: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-group">
                    <Label>Máximo Simultâneo: {settings.agents.maxConcurrent}</Label>
                    <Slider 
                      value={[settings.agents.maxConcurrent]}
                      min={1}
                      max={10}
                      step={1}
                      onValueChange={([v]) => setSettings(prev => ({
                        ...prev,
                        agents: { ...prev.agents, maxConcurrent: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Seleção Automática</Label>
                      <span className="setting-desc">IA escolhe agentes automaticamente</span>
                    </div>
                    <Switch 
                      checked={settings.agents.autoSelect}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        agents: { ...prev.agents, autoSelect: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-group">
                    <Label>Modo de Prioridade</Label>
                    <Select 
                      value={settings.agents.priorityMode}
                      onValueChange={(v) => setSettings(prev => ({
                        ...prev,
                        agents: { ...prev.agents, priorityMode: v }
                      }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="smart">Inteligente</SelectItem>
                        <SelectItem value="fifo">FIFO</SelectItem>
                        <SelectItem value="priority">Por Prioridade</SelectItem>
                        <SelectItem value="round-robin">Round Robin</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="agents-list-section">
                    <h4>Agentes Disponíveis</h4>
                    <div className="agents-grid">
                      {['Planner', 'Research', 'Knowledge', 'Memory', 'Voice', 'Vision', 'Design', 'Development', 'Site Builder', 'App Builder', 'Automation', 'Sales', 'Operations', 'Integration', 'Analytics', 'Security'].map(agent => (
                        <div key={agent} className="agent-item-setting">
                          <Bot className="w-4 h-4" />
                          <span>{agent}</span>
                          <Switch defaultChecked />
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
              
              {/* LEADER AGENT */}
              {activeTab === 'leader' && (
                <div className="settings-section">
                  <h3>Agente Líder / Orquestrador</h3>
                  <p className="section-desc">Coordena todos os agentes e consolida respostas</p>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Agente Líder Ativado</Label>
                      <span className="setting-desc">Orquestração central de agentes</span>
                    </div>
                    <Switch 
                      checked={settings.leader.enabled}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        leader: { ...prev.leader, enabled: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-group">
                    <Label>Nível de Autonomia</Label>
                    <Select 
                      value={settings.leader.autonomyLevel}
                      onValueChange={(v) => setSettings(prev => ({
                        ...prev,
                        leader: { ...prev.leader, autonomyLevel: v }
                      }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="low">Baixo</SelectItem>
                        <SelectItem value="medium">Médio</SelectItem>
                        <SelectItem value="high">Alto</SelectItem>
                        <SelectItem value="full">Total</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="setting-group">
                    <Label>Modo de Consolidação</Label>
                    <Select 
                      value={settings.leader.consolidationMode}
                      onValueChange={(v) => setSettings(prev => ({
                        ...prev,
                        leader: { ...prev.leader, consolidationMode: v }
                      }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="smart">Inteligente</SelectItem>
                        <SelectItem value="merge">Merge</SelectItem>
                        <SelectItem value="best">Melhor Resultado</SelectItem>
                        <SelectItem value="weighted">Ponderado</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="setting-group">
                    <Label>Política de Fallback</Label>
                    <Select 
                      value={settings.leader.fallbackPolicy}
                      onValueChange={(v) => setSettings(prev => ({
                        ...prev,
                        leader: { ...prev.leader, fallbackPolicy: v }
                      }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="retry">Tentar Novamente</SelectItem>
                        <SelectItem value="skip">Pular Agente</SelectItem>
                        <SelectItem value="manual">Manual</SelectItem>
                        <SelectItem value="abort">Abortar</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="leader-capabilities">
                    <h4>Capacidades do Líder</h4>
                    <ul className="capabilities-list">
                      <li><Check className="w-4 h-4" /> Entender intenção do usuário</li>
                      <li><Check className="w-4 h-4" /> Chamar agentes corretos</li>
                      <li><Check className="w-4 h-4" /> Executar múltiplos agentes</li>
                      <li><Check className="w-4 h-4" /> Consolidar resultados</li>
                      <li><Check className="w-4 h-4" /> Priorizar agentes</li>
                      <li><Check className="w-4 h-4" /> Gerenciar conflitos</li>
                      <li><Check className="w-4 h-4" /> Manter contexto global</li>
                    </ul>
                  </div>
                </div>
              )}
              
              {/* MEMORY */}
              {activeTab === 'memory' && (
                <div className="settings-section">
                  <h3>Configurações de Memória</h3>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Memória Ativada</Label>
                      <span className="setting-desc">Lembrar conversas anteriores</span>
                    </div>
                    <Switch 
                      checked={settings.memory.enabled}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        memory: { ...prev.memory, enabled: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-group">
                    <Label>Retenção (dias): {settings.memory.retentionDays}</Label>
                    <Slider 
                      value={[settings.memory.retentionDays]}
                      min={7}
                      max={365}
                      step={7}
                      onValueChange={([v]) => setSettings(prev => ({
                        ...prev,
                        memory: { ...prev.memory, retentionDays: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Memória Pessoal</Label>
                      <span className="setting-desc">Preferências do usuário</span>
                    </div>
                    <Switch 
                      checked={settings.memory.personalMemory}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        memory: { ...prev.memory, personalMemory: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Memória por Projeto</Label>
                      <span className="setting-desc">Contexto por projeto</span>
                    </div>
                    <Switch 
                      checked={settings.memory.projectMemory}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        memory: { ...prev.memory, projectMemory: v }
                      }))}
                    />
                  </div>
                  
                  <Button variant="destructive" size="sm" className="mt-4">
                    <Trash2 className="w-4 h-4 mr-2" />
                    Limpar Memória
                  </Button>
                </div>
              )}
              
              {/* KNOWLEDGE */}
              {activeTab === 'knowledge' && (
                <div className="settings-section">
                  <h3>Base de Conhecimento</h3>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Indexação Automática</Label>
                      <span className="setting-desc">Indexar documentos automaticamente</span>
                    </div>
                    <Switch 
                      checked={settings.knowledge.autoIndex}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        knowledge: { ...prev.knowledge, autoIndex: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Reprocessar ao Atualizar</Label>
                      <span className="setting-desc">Reindexar documentos modificados</span>
                    </div>
                    <Switch 
                      checked={settings.knowledge.reprocessOnUpdate}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        knowledge: { ...prev.knowledge, reprocessOnUpdate: v }
                      }))}
                    />
                  </div>
                  
                  <div className="knowledge-actions">
                    <Button variant="outline" size="sm">
                      <Upload className="w-4 h-4 mr-2" />
                      Upload de Documentos
                    </Button>
                    <Button variant="outline" size="sm">
                      <RefreshCw className="w-4 h-4 mr-2" />
                      Reindexar Base
                    </Button>
                  </div>
                </div>
              )}
              
              {/* AUTOMATION */}
              {activeTab === 'automation' && (
                <div className="settings-section">
                  <h3>Automações</h3>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Automações Ativadas</Label>
                      <span className="setting-desc">Executar workflows automáticos</span>
                    </div>
                    <Switch 
                      checked={settings.automation.enabled}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        automation: { ...prev.automation, enabled: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-group">
                    <Label>Máximo de Triggers: {settings.automation.maxTriggers}</Label>
                    <Slider 
                      value={[settings.automation.maxTriggers]}
                      min={1}
                      max={50}
                      step={1}
                      onValueChange={([v]) => setSettings(prev => ({
                        ...prev,
                        automation: { ...prev.automation, maxTriggers: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Logs de Automação</Label>
                      <span className="setting-desc">Registrar execuções</span>
                    </div>
                    <Switch 
                      checked={settings.automation.loggingEnabled}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        automation: { ...prev.automation, loggingEnabled: v }
                      }))}
                    />
                  </div>
                </div>
              )}
              
              {/* BUILDERS */}
              {activeTab === 'builders' && (
                <div className="settings-section">
                  <h3>Sites e Apps</h3>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Site Builder</Label>
                      <span className="setting-desc">Criar sites automaticamente</span>
                    </div>
                    <Switch 
                      checked={settings.builders.siteBuilderEnabled}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        builders: { ...prev.builders, siteBuilderEnabled: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>App Builder</Label>
                      <span className="setting-desc">Criar apps automaticamente</span>
                    </div>
                    <Switch 
                      checked={settings.builders.appBuilderEnabled}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        builders: { ...prev.builders, appBuilderEnabled: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Preview Automático</Label>
                      <span className="setting-desc">Mostrar preview ao gerar</span>
                    </div>
                    <Switch 
                      checked={settings.builders.autoPreview}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        builders: { ...prev.builders, autoPreview: v }
                      }))}
                    />
                  </div>
                </div>
              )}
              
              {/* SECURITY */}
              {activeTab === 'security' && (
                <div className="settings-section">
                  <h3>Segurança</h3>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Autenticação 2FA</Label>
                      <span className="setting-desc">Verificação em duas etapas</span>
                    </div>
                    <Switch 
                      checked={settings.security.twoFactorEnabled}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        security: { ...prev.security, twoFactorEnabled: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-group">
                    <Label>Timeout de Sessão (minutos): {settings.security.sessionTimeout}</Label>
                    <Slider 
                      value={[settings.security.sessionTimeout]}
                      min={30}
                      max={1440}
                      step={30}
                      onValueChange={([v]) => setSettings(prev => ({
                        ...prev,
                        security: { ...prev.security, sessionTimeout: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>API Keys Permitidas</Label>
                      <span className="setting-desc">Criar chaves de API</span>
                    </div>
                    <Switch 
                      checked={settings.security.apiKeysAllowed}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        security: { ...prev.security, apiKeysAllowed: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Log de Auditoria</Label>
                      <span className="setting-desc">Registrar ações sensíveis</span>
                    </div>
                    <Switch 
                      checked={settings.security.auditLogging}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        security: { ...prev.security, auditLogging: v }
                      }))}
                    />
                  </div>
                </div>
              )}
              
              {/* UPDATES */}
              {activeTab === 'updates' && (
                <div className="settings-section">
                  <h3>Atualizações</h3>
                  
                  <div className="version-info">
                    <span className="version-label">Versão Atual</span>
                    <span className="version-number">ORIONIS v3.0.0</span>
                  </div>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Atualizações Automáticas</Label>
                      <span className="setting-desc">Atualizar automaticamente</span>
                    </div>
                    <Switch 
                      checked={settings.updates.autoUpdates}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        updates: { ...prev.updates, autoUpdates: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-group">
                    <Label>Canal de Atualização</Label>
                    <Select 
                      value={settings.updates.channel}
                      onValueChange={(v) => setSettings(prev => ({
                        ...prev,
                        updates: { ...prev.updates, channel: v }
                      }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="stable">Estável</SelectItem>
                        <SelectItem value="beta">Beta</SelectItem>
                        <SelectItem value="alpha">Alpha</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Rollback Habilitado</Label>
                      <span className="setting-desc">Permitir voltar versão</span>
                    </div>
                    <Switch 
                      checked={settings.updates.rollbackEnabled}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        updates: { ...prev.updates, rollbackEnabled: v }
                      }))}
                    />
                  </div>
                </div>
              )}
              
              {/* ANALYTICS */}
              {activeTab === 'analytics' && (
                <div className="settings-section">
                  <h3>Analytics</h3>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Analytics Ativado</Label>
                      <span className="setting-desc">Coletar métricas de uso</span>
                    </div>
                    <Switch 
                      checked={settings.analytics.enabled}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        analytics: { ...prev.analytics, enabled: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Rastrear Uso</Label>
                      <span className="setting-desc">Métricas de utilização</span>
                    </div>
                    <Switch 
                      checked={settings.analytics.trackUsage}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        analytics: { ...prev.analytics, trackUsage: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Rastrear Custos</Label>
                      <span className="setting-desc">Gastos com API</span>
                    </div>
                    <Switch 
                      checked={settings.analytics.trackCosts}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        analytics: { ...prev.analytics, trackCosts: v }
                      }))}
                    />
                  </div>
                  
                  <div className="setting-row">
                    <div className="setting-info">
                      <Label>Rastrear Performance</Label>
                      <span className="setting-desc">Tempo de resposta</span>
                    </div>
                    <Switch 
                      checked={settings.analytics.trackPerformance}
                      onCheckedChange={(v) => setSettings(prev => ({
                        ...prev,
                        analytics: { ...prev.analytics, trackPerformance: v }
                      }))}
                    />
                  </div>
                </div>
              )}
            </ScrollArea>
          </div>
        </div>
      </div>
    </div>
  );
};

// ============== AGENTS PANEL ==============
const AgentsPanel = ({ isOpen, onClose }) => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    if (isOpen) {
      loadAgents();
    }
  }, [isOpen]);
  
  const loadAgents = async () => {
    try {
      const response = await axios.get(`${API}/system/status`, { withCredentials: true });
      setAgents(response.data.agents || []);
    } catch (error) {
      console.error('Error loading agents:', error);
    } finally {
      setLoading(false);
    }
  };
  
  if (!isOpen) return null;
  
  return (
    <div className="agents-panel-overlay" data-testid="agents-panel">
      <div className="agents-panel">
        <div className="panel-header">
          <div className="panel-title">
            <Users className="w-5 h-5" />
            <span>Sistema de Agentes</span>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="w-5 h-5" />
          </Button>
        </div>
        
        <div className="panel-content">
          {/* Leader Agent */}
          <div className="leader-agent-section">
            <div className="leader-header">
              <Crown className="w-5 h-5 text-amber-400" />
              <span>Agente Líder / Orquestrador</span>
              <span className="status-badge active">ATIVO</span>
            </div>
            <p className="leader-desc">Coordena todos os agentes e consolida respostas</p>
          </div>
          
          {/* Agents Grid */}
          <div className="agents-grid-panel">
            {loading ? (
              <div className="loading-agents">
                <Loader2 className="w-6 h-6 animate-spin" />
                <span>Carregando agentes...</span>
              </div>
            ) : (
              agents.map((agent, idx) => (
                <div key={agent.name || idx} className={`agent-card ${agent.status}`}>
                  <div className="agent-icon">
                    <Bot className="w-5 h-5" />
                  </div>
                  <div className="agent-info">
                    <span className="agent-name">{agent.name}</span>
                    <span className="agent-type">{agent.type}</span>
                  </div>
                  <span className={`agent-status ${agent.status}`}>
                    {agent.status === 'active' ? 'Ativo' : 'Standby'}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// ============== LANDING PAGE ==============
const LandingPage = () => {
  const navigate = useNavigate();
  const [systemStatus, setSystemStatus] = useState(null);
  
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await axios.get(`${API}/auth/me`, { withCredentials: true });
        if (response.data) {
          navigate('/dashboard', { state: { user: response.data } });
        }
      } catch (error) {}
    };
    checkAuth();
    
    axios.get(`${API}/system/status`).then(res => setSystemStatus(res.data)).catch(() => {});
  }, [navigate]);
  
  const handleLogin = () => {
    const redirectUrl = window.location.origin + '/dashboard';
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };
  
  return (
    <div className="landing-container" data-testid="landing-page">
      <div className="hex-grid" />
      <div className="scan-lines" />
      <div className="data-streams" />
      
      <div className="landing-content">
        <header className="landing-header">
          <div className="logo-container">
            <span className="logo-text">ORIONIS</span>
            <span className="logo-version">v3.0</span>
          </div>
          <Button onClick={handleLogin} className="login-btn" data-testid="login-btn">
            <Zap className="w-4 h-4 mr-2" />
            Entrar
          </Button>
        </header>
        
        <main className="hero-section">
          <div className="orb-container-landing">
            <NeuralOrb3D state="idle" size="xlarge" />
          </div>
          
          <h1 className="hero-title">
            <span className="title-main">ORIONIS</span>
            <span className="title-sub">Orion Intelligent System</span>
          </h1>
          
          <p className="hero-description">
            Sistema operacional de inteligência artificial universal.
            Pense. Pesquise. Crie. Construa. Automatize.
          </p>
          
          <Button onClick={handleLogin} className="cta-btn" data-testid="get-started-btn">
            <Sparkles className="w-5 h-5 mr-2" />
            Iniciar Sistema
          </Button>
        </main>
        
        <div className="status-panels">
          <div className="status-panel panel-left">
            <div className="panel-header">
              <Cpu className="w-4 h-4" />
              <span>SYSTEM STATUS</span>
            </div>
            <div className="panel-content">
              <div className="status-item">
                <span className="status-label">Core</span>
                <span className="status-value online">ONLINE</span>
              </div>
              <div className="status-item">
                <span className="status-label">Neural</span>
                <span className="status-value online">ACTIVE</span>
              </div>
              <div className="status-item">
                <span className="status-label">Memory</span>
                <span className="status-value">READY</span>
              </div>
            </div>
          </div>
          
          <div className="status-panel panel-right">
            <div className="panel-header">
              <Activity className="w-4 h-4" />
              <span>ACTIVE AGENTS</span>
            </div>
            <div className="panel-content">
              {systemStatus?.agents?.slice(0, 4).map((agent, idx) => (
                <div key={idx} className="agent-item">
                  <span className={`agent-dot ${agent.status}`} />
                  <span className="agent-name">{agent.name}</span>
                </div>
              )) || (
                <>
                  <div className="agent-item"><span className="agent-dot active" /><span className="agent-name">Core Orchestrator</span></div>
                  <div className="agent-item"><span className="agent-dot active" /><span className="agent-name">Research Agent</span></div>
                  <div className="agent-item"><span className="agent-dot active" /><span className="agent-name">Voice Agent</span></div>
                  <div className="agent-item"><span className="agent-dot active" /><span className="agent-name">Vision Agent</span></div>
                </>
              )}
            </div>
          </div>
        </div>
        
        <div className="features-grid">
          {[
            { icon: MessageSquare, title: 'Chat IA', desc: 'Conversas inteligentes com contexto' },
            { icon: Mic, title: 'Comando por Voz', desc: 'Transcrição e síntese em tempo real' },
            { icon: Eye, title: 'Visão Computacional', desc: 'Análise de imagens e câmera' },
            { icon: Image, title: 'Geração de Imagens', desc: 'Criação de imagens com IA' }
          ].map((feature, idx) => (
            <div key={idx} className="feature-card">
              <feature.icon className="feature-icon" />
              <h3>{feature.title}</h3>
              <p>{feature.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// ============== DASHBOARD ==============
const Dashboard = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [user, setUser] = useState(location.state?.user || null);
  const [loading, setLoading] = useState(!location.state?.user);
  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [showCamera, setShowCamera] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null);
  const [showImageGen, setShowImageGen] = useState(false);
  const [generatedImage, setGeneratedImage] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [systemStatus, setSystemStatus] = useState(null);
  const [showSettings, setShowSettings] = useState(false);
  const [showAgents, setShowAgents] = useState(false);
  const [systemState, setSystemState] = useState('idle');
  const [activeAgents, setActiveAgents] = useState([]);
  const [voiceSettings, setVoiceSettings] = useState({ enabled: true, autoSpeak: false, voice: 'nova' });
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const audioRef = useRef(null);
  
  useEffect(() => {
    if (user) {
      setLoading(false);
      return;
    }
    
    const checkAuth = async () => {
      try {
        const response = await axios.get(`${API}/auth/me`, { withCredentials: true });
        setUser(response.data);
      } catch (error) {
        navigate('/');
      } finally {
        setLoading(false);
      }
    };
    checkAuth();
  }, [user, navigate]);
  
  useEffect(() => {
    if (!user) return;
    
    axios.get(`${API}/conversations`, { withCredentials: true })
      .then(res => setConversations(res.data))
      .catch(() => {});
    
    axios.get(`${API}/system/status`, { withCredentials: true })
      .then(res => setSystemStatus(res.data))
      .catch(() => {});
  }, [user]);
  
  useEffect(() => {
    if (!activeConversation) {
      setMessages([]);
      return;
    }
    
    axios.get(`${API}/conversations/${activeConversation}/messages`, { withCredentials: true })
      .then(res => setMessages(res.data))
      .catch(() => {});
  }, [activeConversation]);
  
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);
  
  const handleLogout = async () => {
    try {
      await axios.post(`${API}/auth/logout`, {}, { withCredentials: true });
      navigate('/');
    } catch (error) {
      navigate('/');
    }
  };
  
  const sendMessage = async (text = input, imageBase64 = capturedImage) => {
    if (!text.trim() && !imageBase64) return;
    
    const messageText = text.trim();
    setInput('');
    setCapturedImage(null);
    setIsSending(true);
    setIsTyping(true);
    setSystemState('thinking');
    setActiveAgents([{ name: 'Core', display_name: 'Core Orchestrator' }]);
    
    const userMsg = {
      message_id: Date.now().toString(),
      role: 'user',
      content: messageText,
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMsg]);
    
    try {
      const response = await axios.post(`${API}/chat`, {
        message: messageText,
        conversation_id: activeConversation,
        image_base64: imageBase64
      }, { withCredentials: true });
      
      const assistantMsg = {
        message_id: Date.now().toString() + '_assistant',
        role: 'assistant',
        content: response.data.message,
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, assistantMsg]);
      
      if (!activeConversation) {
        setActiveConversation(response.data.conversation_id);
        const convRes = await axios.get(`${API}/conversations`, { withCredentials: true });
        setConversations(convRes.data);
      }
      
      // Auto speak if enabled
      if (voiceSettings.autoSpeak && voiceSettings.enabled) {
        speakText(response.data.message);
      }
    } catch (error) {
      toast.error('Erro ao enviar mensagem');
      console.error(error);
    } finally {
      setIsSending(false);
      setIsTyping(false);
      setSystemState('idle');
      setActiveAgents([]);
    }
  };
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };
  
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];
      
      mediaRecorderRef.current.ondataavailable = (e) => {
        audioChunksRef.current.push(e.data);
      };
      
      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        stream.getTracks().forEach(track => track.stop());
        
        setSystemState('listening');
        
        const formData = new FormData();
        formData.append('file', audioBlob, 'audio.webm');
        
        try {
          const response = await axios.post(`${API}/voice/transcribe`, formData, {
            withCredentials: true,
            headers: { 'Content-Type': 'multipart/form-data' }
          });
          setInput(response.data.text);
          toast.success('Áudio transcrito');
        } catch (error) {
          toast.error('Erro na transcrição');
        } finally {
          setSystemState('idle');
        }
      };
      
      mediaRecorderRef.current.start();
      setIsRecording(true);
      setSystemState('listening');
      toast.info('Gravando...');
    } catch (error) {
      toast.error('Erro ao acessar microfone');
    }
  };
  
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };
  
  const speakText = async (text) => {
    if (isSpeaking) {
      audioRef.current?.pause();
      setIsSpeaking(false);
      setSystemState('idle');
      return;
    }
    
    try {
      setIsSpeaking(true);
      setSystemState('speaking');
      
      const response = await axios.post(`${API}/voice/speak`, {
        text: text.substring(0, 500),
        voice: voiceSettings.voice || 'nova'
      }, { withCredentials: true });
      
      const audio = new Audio(`data:audio/mp3;base64,${response.data.audio_base64}`);
      audioRef.current = audio;
      audio.onended = () => {
        setIsSpeaking(false);
        setSystemState('idle');
      };
      audio.play();
    } catch (error) {
      toast.error('Erro ao sintetizar voz');
      setIsSpeaking(false);
      setSystemState('idle');
    }
  };
  
  const startCamera = async () => {
    setShowCamera(true);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (error) {
      toast.error('Erro ao acessar câmera');
      setShowCamera(false);
    }
  };
  
  const captureImage = () => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current;
      const video = videoRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas.getContext('2d').drawImage(video, 0, 0);
      
      const imageData = canvas.toDataURL('image/jpeg').split(',')[1];
      setCapturedImage(imageData);
      
      const stream = video.srcObject;
      stream?.getTracks().forEach(track => track.stop());
      setShowCamera(false);
      
      toast.success('Imagem capturada');
    }
  };
  
  const closeCamera = () => {
    if (videoRef.current?.srcObject) {
      videoRef.current.srcObject.getTracks().forEach(track => track.stop());
    }
    setShowCamera(false);
  };
  
  const generateImage = async (prompt) => {
    setIsGenerating(true);
    setSystemState('creating');
    setActiveAgents([{ name: 'Design', display_name: 'Design Agent' }]);
    
    try {
      const response = await axios.post(`${API}/image/generate`, {
        prompt: prompt
      }, { withCredentials: true });
      
      setGeneratedImage(response.data.image_base64);
      toast.success('Imagem gerada!');
    } catch (error) {
      toast.error('Erro ao gerar imagem');
    } finally {
      setIsGenerating(false);
      setSystemState('idle');
      setActiveAgents([]);
    }
  };
  
  const newConversation = () => {
    setActiveConversation(null);
    setMessages([]);
    inputRef.current?.focus();
  };
  
  const deleteConversation = async (convId) => {
    try {
      await axios.delete(`${API}/conversations/${convId}`, { withCredentials: true });
      setConversations(prev => prev.filter(c => c.conversation_id !== convId));
      if (activeConversation === convId) {
        setActiveConversation(null);
        setMessages([]);
      }
      toast.success('Conversa excluída');
    } catch (error) {
      toast.error('Erro ao excluir');
    }
  };
  
  if (loading) {
    return (
      <div className="min-h-screen bg-[#000a14] flex items-center justify-center">
        <NeuralOrb3D state="thinking" size="large" />
      </div>
    );
  }
  
  return (
    <div className="dashboard-container" data-testid="dashboard">
      <div className="hex-grid" />
      <div className="scan-lines" />
      
      {/* Settings Panel */}
      <SettingsPanel isOpen={showSettings} onClose={() => setShowSettings(false)} user={user} />
      
      {/* Agents Panel */}
      <AgentsPanel isOpen={showAgents} onClose={() => setShowAgents(false)} />
      
      {/* Camera Modal */}
      {showCamera && (
        <div className="modal-overlay" data-testid="camera-modal">
          <div className="camera-modal">
            <div className="modal-header">
              <span>Câmera - ORIONIS Vision</span>
              <Button variant="ghost" size="icon" onClick={closeCamera}>
                <X className="w-4 h-4" />
              </Button>
            </div>
            <video ref={videoRef} autoPlay playsInline className="camera-preview" />
            <canvas ref={canvasRef} className="hidden" />
            <div className="camera-controls">
              <Button onClick={captureImage} className="capture-btn" data-testid="capture-btn">
                <Camera className="w-5 h-5 mr-2" />
                Capturar
              </Button>
            </div>
          </div>
        </div>
      )}
      
      {/* Image Gen Modal */}
      {showImageGen && (
        <div className="modal-overlay" data-testid="image-gen-modal">
          <div className="image-gen-modal">
            <div className="modal-header">
              <span>Geração de Imagem - ORIONIS Design</span>
              <Button variant="ghost" size="icon" onClick={() => setShowImageGen(false)}>
                <X className="w-4 h-4" />
              </Button>
            </div>
            <div className="image-gen-content">
              <input
                type="text"
                placeholder="Descreva a imagem que deseja criar..."
                className="image-prompt-input"
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && e.target.value.trim()) {
                    generateImage(e.target.value.trim());
                  }
                }}
                data-testid="image-prompt-input"
              />
              {isGenerating ? (
                <div className="generating-loader">
                  <NeuralOrb3D state="creating" size="medium" />
                  <p>Gerando imagem...</p>
                </div>
              ) : generatedImage ? (
                <div className="generated-image-container">
                  <img src={`data:image/png;base64,${generatedImage}`} alt="Generated" className="generated-image" />
                  <Button onClick={() => {
                    const link = document.createElement('a');
                    link.href = `data:image/png;base64,${generatedImage}`;
                    link.download = 'orionis-generated.png';
                    link.click();
                  }} className="download-btn">
                    Download
                  </Button>
                </div>
              ) : (
                <div className="image-placeholder">
                  <Sparkles className="w-12 h-12 text-cyan-400/50" />
                  <p>Digite um prompt e pressione Enter</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      
      {/* Sidebar */}
      <aside className="sidebar" data-testid="sidebar">
        <div className="sidebar-header">
          <div className="logo-small">
            <Brain className="w-6 h-6 text-cyan-400" />
            <span>ORIONIS</span>
          </div>
          <Button variant="ghost" size="icon" onClick={newConversation} className="new-chat-btn" data-testid="new-chat-btn">
            <Plus className="w-5 h-5" />
          </Button>
        </div>
        
        <ScrollArea className="conversations-list">
          {conversations.map(conv => (
            <div 
              key={conv.conversation_id}
              className={`conversation-item ${activeConversation === conv.conversation_id ? 'active' : ''}`}
              onClick={() => setActiveConversation(conv.conversation_id)}
              data-testid={`conversation-${conv.conversation_id}`}
            >
              <MessageSquare className="w-4 h-4" />
              <span className="conv-title">{conv.title}</span>
              <Button variant="ghost" size="icon" className="delete-btn" onClick={(e) => { e.stopPropagation(); deleteConversation(conv.conversation_id); }}>
                <Trash2 className="w-3 h-3" />
              </Button>
            </div>
          ))}
        </ScrollArea>
        
        <div className="sidebar-footer">
          <div className="user-info">
            {user?.picture ? (
              <img src={user.picture} alt={user.name} className="user-avatar" />
            ) : (
              <div className="user-avatar-placeholder">{user?.name?.charAt(0) || 'U'}</div>
            )}
            <div className="user-details">
              <span className="user-name">{user?.name}</span>
              <span className="user-email">{user?.email}</span>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={handleLogout} className="logout-btn" data-testid="logout-btn">
            <LogOut className="w-4 h-4" />
          </Button>
        </div>
      </aside>
      
      {/* Main Chat Area */}
      <main className="chat-main">
        {/* Top Bar */}
        <div className="top-bar">
          <div className="status-indicators">
            <div className="status-item">
              <span className={`status-dot ${systemState === 'idle' ? 'online' : 'active'}`} />
              <span>{systemState === 'idle' ? 'CORE ONLINE' : systemState.toUpperCase()}</span>
            </div>
            <div className="status-item">
              <Cpu className="w-4 h-4" />
              <span>GPT-4o</span>
            </div>
            <div className="status-item">
              <Activity className="w-4 h-4" />
              <span>{activeAgents.length > 0 ? `${activeAgents.length} AGENT${activeAgents.length > 1 ? 'S' : ''}` : 'READY'}</span>
            </div>
          </div>
          
          <div className="tool-buttons">
            <Button variant="ghost" size="icon" onClick={() => setShowAgents(true)} className="tool-btn" data-testid="agents-btn" title="Agentes">
              <Users className="w-5 h-5" />
            </Button>
            <Button variant="ghost" size="icon" onClick={startCamera} className="tool-btn" data-testid="camera-btn" title="Câmera">
              <Camera className="w-5 h-5" />
            </Button>
            <Button variant="ghost" size="icon" onClick={() => setShowImageGen(true)} className="tool-btn" data-testid="image-gen-btn" title="Gerar Imagem">
              <Image className="w-5 h-5" />
            </Button>
            <Button variant="ghost" size="icon" onClick={() => setShowSettings(true)} className="tool-btn settings-btn" data-testid="settings-btn" title="Configurações">
              <MoreVertical className="w-5 h-5" />
            </Button>
          </div>
        </div>
        
        {/* Messages Area */}
        <ScrollArea className="messages-area" data-testid="messages-area">
          {messages.length === 0 ? (
            <div className="welcome-screen">
              <div className="welcome-orb">
                <NeuralOrb3D state={systemState} size="large" activeAgents={activeAgents} />
              </div>
              <h2>ORIONIS Online</h2>
              <p>Como posso ajudá-lo hoje?</p>
              <div className="quick-actions">
                <Button variant="outline" onClick={() => setInput('ORIONIS, me ajude a planejar um projeto')} className="quick-btn">
                  <Brain className="w-4 h-4 mr-2" />
                  Planejamento
                </Button>
                <Button variant="outline" onClick={() => setInput('ORIONIS, pesquise sobre')} className="quick-btn">
                  <Search className="w-4 h-4 mr-2" />
                  Pesquisa
                </Button>
                <Button variant="outline" onClick={() => setShowImageGen(true)} className="quick-btn">
                  <Sparkles className="w-4 h-4 mr-2" />
                  Criar Imagem
                </Button>
              </div>
            </div>
          ) : (
            <div className="messages-container">
              {messages.map((msg, idx) => (
                <div key={msg.message_id || idx} className={`message ${msg.role}`} data-testid={`message-${msg.role}`}>
                  <div className="message-avatar">
                    {msg.role === 'user' ? (
                      user?.picture ? <img src={user.picture} alt="User" /> : <div className="avatar-placeholder">{user?.name?.charAt(0)}</div>
                    ) : (
                      <div className="orionis-avatar"><Brain className="w-5 h-5" /></div>
                    )}
                  </div>
                  <div className="message-content">
                    <div className="message-header">
                      <span className="sender-name">{msg.role === 'user' ? user?.name : 'ORIONIS'}</span>
                    </div>
                    <div className="message-text">{msg.content}</div>
                    {msg.role === 'assistant' && (
                      <div className="message-actions">
                        <Button variant="ghost" size="sm" onClick={() => speakText(msg.content)} className="speak-btn">
                          {isSpeaking ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {isTyping && (
                <div className="message assistant typing">
                  <div className="message-avatar">
                    <div className="orionis-avatar"><Brain className="w-5 h-5" /></div>
                  </div>
                  <div className="message-content">
                    <div className="typing-indicator"><span /><span /><span /></div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </ScrollArea>
        
        {/* Captured Image Preview */}
        {capturedImage && (
          <div className="captured-preview">
            <img src={`data:image/jpeg;base64,${capturedImage}`} alt="Captured" />
            <Button variant="ghost" size="icon" onClick={() => setCapturedImage(null)} className="remove-capture">
              <X className="w-4 h-4" />
            </Button>
          </div>
        )}
        
        {/* Input Area */}
        <div className="input-area" data-testid="input-area">
          <div className="input-container">
            <Button variant="ghost" size="icon" onClick={isRecording ? stopRecording : startRecording} className={`mic-btn ${isRecording ? 'recording' : ''}`} data-testid="mic-btn">
              {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
            </Button>
            
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="ORIONIS, ..."
              className="chat-input"
              rows={1}
              data-testid="chat-input"
            />
            
            <Button onClick={() => sendMessage()} disabled={isSending || (!input.trim() && !capturedImage)} className="send-btn" data-testid="send-btn">
              {isSending ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
            </Button>
          </div>
        </div>
      </main>
      
      {/* Right Panel */}
      <aside className="right-panel" data-testid="right-panel">
        {/* Neural Orb Status */}
        <div className="neural-status-panel">
          <NeuralOrb3D state={systemState} size="small" activeAgents={activeAgents} />
          <span className="neural-status-text">{systemState.toUpperCase()}</span>
        </div>
        
        <div className="panel-section">
          <div className="panel-title">
            <Cpu className="w-4 h-4" />
            <span>SYSTEM ANALYTICS</span>
          </div>
          <div className="analytics-grid">
            <div className="analytic-item">
              <span className="analytic-label">Response</span>
              <span className="analytic-value">~2s</span>
            </div>
            <div className="analytic-item">
              <span className="analytic-label">Model</span>
              <span className="analytic-value">GPT-4o</span>
            </div>
            <div className="analytic-item">
              <span className="analytic-label">Memory</span>
              <span className="analytic-value">Active</span>
            </div>
            <div className="analytic-item">
              <span className="analytic-label">Status</span>
              <span className="analytic-value online">Online</span>
            </div>
          </div>
        </div>
        
        <div className="panel-section">
          <div className="panel-title">
            <Zap className="w-4 h-4" />
            <span>ACTIVE MODULES</span>
          </div>
          <div className="modules-list">
            <div className="module-item active"><MessageSquare className="w-4 h-4" /><span>Chat Engine</span></div>
            <div className="module-item active"><Mic className="w-4 h-4" /><span>Voice Agent</span></div>
            <div className="module-item active"><Eye className="w-4 h-4" /><span>Vision Agent</span></div>
            <div className="module-item active"><Sparkles className="w-4 h-4" /><span>Design Agent</span></div>
          </div>
        </div>
        
        <div className="panel-section capabilities">
          <div className="panel-title">
            <Brain className="w-4 h-4" />
            <span>CAPABILITIES</span>
          </div>
          <div className="capabilities-list">
            {['Chat', 'Voice', 'Vision', 'Image Gen', 'Research', 'Analysis', 'STR', 'API'].map(cap => (
              <span key={cap} className="capability-tag">{cap}</span>
            ))}
          </div>
        </div>
      </aside>
      
      <Toaster position="top-right" />
    </div>
  );
};

// ============== APP ==============
function App() {
  return (
    <BrowserRouter>
      <SystemStateProvider>
        <AuthContext>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/dashboard" element={<Dashboard />} />
          </Routes>
        </AuthContext>
      </SystemStateProvider>
    </BrowserRouter>
  );
}

export default App;
