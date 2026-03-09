import { useState, useEffect, useRef, useCallback } from "react";
import { BrowserRouter, Routes, Route, useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import "@/App.css";
import { Toaster } from "@/components/ui/sonner";
import { toast } from "sonner";
import { 
  Mic, MicOff, Camera, Send, Volume2, VolumeX, Image, 
  MessageSquare, Settings, LogOut, Trash2, Plus, X,
  Zap, Brain, Eye, Sparkles, Activity, Cpu, Loader2
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// ============== AUTH CONTEXT ==============
const AuthContext = ({ children }) => {
  const location = useLocation();
  
  // CRITICAL: If returning from OAuth callback, let AuthCallback handle it
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
        
        // Clear the hash and navigate to dashboard with user data
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
        <OrbLoader />
        <p className="text-cyan-400 mt-4 font-mono">Autenticando...</p>
      </div>
    </div>
  );
};

// ============== ORB LOADER ==============
const OrbLoader = () => (
  <div className="orb-loader">
    <div className="orb-core" />
    <div className="orb-ring orb-ring-1" />
    <div className="orb-ring orb-ring-2" />
    <div className="orb-ring orb-ring-3" />
  </div>
);

// ============== LANDING PAGE ==============
const LandingPage = () => {
  const navigate = useNavigate();
  const [systemStatus, setSystemStatus] = useState(null);
  
  useEffect(() => {
    // Check if already authenticated
    const checkAuth = async () => {
      try {
        const response = await axios.get(`${API}/auth/me`, { withCredentials: true });
        if (response.data) {
          navigate('/dashboard', { state: { user: response.data } });
        }
      } catch (error) {
        // Not authenticated, stay on landing
      }
    };
    checkAuth();
    
    // Get system status
    axios.get(`${API}/system/status`).then(res => setSystemStatus(res.data)).catch(() => {});
  }, [navigate]);
  
  const handleLogin = () => {
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    const redirectUrl = window.location.origin + '/dashboard';
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };
  
  return (
    <div className="landing-container" data-testid="landing-page">
      {/* Background Effects */}
      <div className="hex-grid" />
      <div className="scan-lines" />
      <div className="data-streams" />
      
      {/* Main Content */}
      <div className="landing-content">
        {/* Header */}
        <header className="landing-header">
          <div className="logo-container">
            <span className="logo-text">ORIONIS</span>
            <span className="logo-version">v3.0</span>
          </div>
          <Button 
            onClick={handleLogin} 
            className="login-btn"
            data-testid="login-btn"
          >
            <Zap className="w-4 h-4 mr-2" />
            Entrar
          </Button>
        </header>
        
        {/* Hero Section */}
        <main className="hero-section">
          <div className="orb-container">
            <div className="main-orb">
              <div className="orb-core">
                <Brain className="w-16 h-16 text-cyan-400" />
              </div>
              <div className="orb-glow" />
            </div>
            <div className="orbit-ring orbit-ring-1">
              <div className="orbit-particle" style={{"--delay": "0s"}} />
              <div className="orbit-particle" style={{"--delay": "1s"}} />
              <div className="orbit-particle" style={{"--delay": "2s"}} />
            </div>
            <div className="orbit-ring orbit-ring-2">
              <div className="orbit-particle" style={{"--delay": "0.5s"}} />
              <div className="orbit-particle" style={{"--delay": "1.5s"}} />
              <div className="orbit-particle" style={{"--delay": "2.5s"}} />
            </div>
            <div className="orbit-ring orbit-ring-3">
              <div className="orbit-particle" style={{"--delay": "0.25s"}} />
              <div className="orbit-particle" style={{"--delay": "1.25s"}} />
            </div>
            
            {/* Scanner Arc */}
            <div className="scanner-arc" />
          </div>
          
          <h1 className="hero-title">
            <span className="title-main">ORIONIS</span>
            <span className="title-sub">Orion Intelligent System</span>
          </h1>
          
          <p className="hero-description">
            Sistema operacional de inteligência artificial universal.
            Pense. Pesquise. Crie. Construa. Automatize.
          </p>
          
          <Button 
            onClick={handleLogin} 
            className="cta-btn"
            data-testid="get-started-btn"
          >
            <Sparkles className="w-5 h-5 mr-2" />
            Iniciar Sistema
          </Button>
        </main>
        
        {/* Status Panels */}
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
                  <div className="agent-item">
                    <span className="agent-dot active" />
                    <span className="agent-name">Core Orchestrator</span>
                  </div>
                  <div className="agent-item">
                    <span className="agent-dot active" />
                    <span className="agent-name">Research Agent</span>
                  </div>
                  <div className="agent-item">
                    <span className="agent-dot active" />
                    <span className="agent-name">Voice Agent</span>
                  </div>
                  <div className="agent-item">
                    <span className="agent-dot active" />
                    <span className="agent-name">Vision Agent</span>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
        
        {/* Features Grid */}
        <div className="features-grid">
          <div className="feature-card">
            <MessageSquare className="feature-icon" />
            <h3>Chat IA</h3>
            <p>Conversas inteligentes com contexto persistente</p>
          </div>
          <div className="feature-card">
            <Mic className="feature-icon" />
            <h3>Comando por Voz</h3>
            <p>Transcrição e síntese de voz em tempo real</p>
          </div>
          <div className="feature-card">
            <Eye className="feature-icon" />
            <h3>Visão Computacional</h3>
            <p>Análise de imagens e câmera ao vivo</p>
          </div>
          <div className="feature-card">
            <Image className="feature-icon" />
            <h3>Geração de Imagens</h3>
            <p>Criação de imagens com IA avançada</p>
          </div>
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
  const [showSidebar, setShowSidebar] = useState(true);
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const audioRef = useRef(null);
  
  // Check auth on mount
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
  
  // Load conversations and system status
  useEffect(() => {
    if (!user) return;
    
    axios.get(`${API}/conversations`, { withCredentials: true })
      .then(res => setConversations(res.data))
      .catch(() => {});
    
    axios.get(`${API}/system/status`, { withCredentials: true })
      .then(res => setSystemStatus(res.data))
      .catch(() => {});
  }, [user]);
  
  // Load messages when conversation changes
  useEffect(() => {
    if (!activeConversation) {
      setMessages([]);
      return;
    }
    
    axios.get(`${API}/conversations/${activeConversation}/messages`, { withCredentials: true })
      .then(res => setMessages(res.data))
      .catch(() => {});
  }, [activeConversation]);
  
  // Scroll to bottom
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
    
    // Add user message optimistically
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
        // Refresh conversations
        const convRes = await axios.get(`${API}/conversations`, { withCredentials: true });
        setConversations(convRes.data);
      }
    } catch (error) {
      toast.error('Erro ao enviar mensagem');
      console.error(error);
    } finally {
      setIsSending(false);
      setIsTyping(false);
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
        
        // Transcribe
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
        }
      };
      
      mediaRecorderRef.current.start();
      setIsRecording(true);
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
      return;
    }
    
    try {
      setIsSpeaking(true);
      const response = await axios.post(`${API}/voice/speak`, {
        text: text.substring(0, 500),
        voice: 'nova'
      }, { withCredentials: true });
      
      const audio = new Audio(`data:audio/mp3;base64,${response.data.audio_base64}`);
      audioRef.current = audio;
      audio.onended = () => setIsSpeaking(false);
      audio.play();
    } catch (error) {
      toast.error('Erro ao sintetizar voz');
      setIsSpeaking(false);
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
      
      // Stop camera
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
        <OrbLoader />
      </div>
    );
  }
  
  return (
    <div className="dashboard-container" data-testid="dashboard">
      {/* Background Effects */}
      <div className="hex-grid" />
      <div className="scan-lines" />
      
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
                  <OrbLoader />
                  <p>Gerando imagem...</p>
                </div>
              ) : generatedImage ? (
                <div className="generated-image-container">
                  <img 
                    src={`data:image/png;base64,${generatedImage}`} 
                    alt="Generated" 
                    className="generated-image"
                  />
                  <Button 
                    onClick={() => {
                      const link = document.createElement('a');
                      link.href = `data:image/png;base64,${generatedImage}`;
                      link.download = 'orionis-generated.png';
                      link.click();
                    }}
                    className="download-btn"
                  >
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
      <aside className={`sidebar ${showSidebar ? 'open' : 'closed'}`} data-testid="sidebar">
        <div className="sidebar-header">
          <div className="logo-small">
            <Brain className="w-6 h-6 text-cyan-400" />
            <span>ORIONIS</span>
          </div>
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={newConversation}
            className="new-chat-btn"
            data-testid="new-chat-btn"
          >
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
              <Button 
                variant="ghost" 
                size="icon"
                className="delete-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  deleteConversation(conv.conversation_id);
                }}
              >
                <Trash2 className="w-3 h-3" />
              </Button>
            </div>
          ))}
        </ScrollArea>
        
        {/* User Info */}
        <div className="sidebar-footer">
          <div className="user-info">
            {user?.picture ? (
              <img src={user.picture} alt={user.name} className="user-avatar" />
            ) : (
              <div className="user-avatar-placeholder">
                {user?.name?.charAt(0) || 'U'}
              </div>
            )}
            <div className="user-details">
              <span className="user-name">{user?.name}</span>
              <span className="user-email">{user?.email}</span>
            </div>
          </div>
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={handleLogout}
            className="logout-btn"
            data-testid="logout-btn"
          >
            <LogOut className="w-4 h-4" />
          </Button>
        </div>
      </aside>
      
      {/* Main Chat Area */}
      <main className="chat-main">
        {/* Top Status Bar */}
        <div className="top-bar">
          <div className="status-indicators">
            <div className="status-item">
              <span className="status-dot online" />
              <span>CORE ONLINE</span>
            </div>
            <div className="status-item">
              <Cpu className="w-4 h-4" />
              <span>GPT-4o</span>
            </div>
            <div className="status-item">
              <Activity className="w-4 h-4" />
              <span>READY</span>
            </div>
          </div>
          
          <div className="tool-buttons">
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={startCamera}
              className="tool-btn"
              data-testid="camera-btn"
            >
              <Camera className="w-5 h-5" />
            </Button>
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={() => setShowImageGen(true)}
              className="tool-btn"
              data-testid="image-gen-btn"
            >
              <Image className="w-5 h-5" />
            </Button>
          </div>
        </div>
        
        {/* Messages Area */}
        <ScrollArea className="messages-area" data-testid="messages-area">
          {messages.length === 0 ? (
            <div className="welcome-screen">
              <div className="welcome-orb">
                <div className="orb-core-small">
                  <Brain className="w-12 h-12 text-cyan-400" />
                </div>
                <div className="orb-pulse" />
              </div>
              <h2>ORIONIS Online</h2>
              <p>Como posso ajudá-lo hoje?</p>
              <div className="quick-actions">
                <Button 
                  variant="outline" 
                  onClick={() => setInput('ORIONIS, me ajude a planejar um projeto')}
                  className="quick-btn"
                >
                  <Brain className="w-4 h-4 mr-2" />
                  Planejamento
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => setInput('ORIONIS, pesquise sobre')}
                  className="quick-btn"
                >
                  <Eye className="w-4 h-4 mr-2" />
                  Pesquisa
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => setShowImageGen(true)}
                  className="quick-btn"
                >
                  <Sparkles className="w-4 h-4 mr-2" />
                  Criar Imagem
                </Button>
              </div>
            </div>
          ) : (
            <div className="messages-container">
              {messages.map((msg, idx) => (
                <div 
                  key={msg.message_id || idx} 
                  className={`message ${msg.role}`}
                  data-testid={`message-${msg.role}`}
                >
                  <div className="message-avatar">
                    {msg.role === 'user' ? (
                      user?.picture ? (
                        <img src={user.picture} alt="User" />
                      ) : (
                        <div className="avatar-placeholder">{user?.name?.charAt(0)}</div>
                      )
                    ) : (
                      <div className="orionis-avatar">
                        <Brain className="w-5 h-5" />
                      </div>
                    )}
                  </div>
                  <div className="message-content">
                    <div className="message-header">
                      <span className="sender-name">
                        {msg.role === 'user' ? user?.name : 'ORIONIS'}
                      </span>
                    </div>
                    <div className="message-text">{msg.content}</div>
                    {msg.role === 'assistant' && (
                      <div className="message-actions">
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => speakText(msg.content)}
                          className="speak-btn"
                        >
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
                    <div className="orionis-avatar">
                      <Brain className="w-5 h-5" />
                    </div>
                  </div>
                  <div className="message-content">
                    <div className="typing-indicator">
                      <span /><span /><span />
                    </div>
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
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={() => setCapturedImage(null)}
              className="remove-capture"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        )}
        
        {/* Input Area */}
        <div className="input-area" data-testid="input-area">
          <div className="input-container">
            <Button
              variant="ghost"
              size="icon"
              onClick={isRecording ? stopRecording : startRecording}
              className={`mic-btn ${isRecording ? 'recording' : ''}`}
              data-testid="mic-btn"
            >
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
            
            <Button
              onClick={() => sendMessage()}
              disabled={isSending || (!input.trim() && !capturedImage)}
              className="send-btn"
              data-testid="send-btn"
            >
              {isSending ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </Button>
          </div>
        </div>
      </main>
      
      {/* Right Panel - System Status */}
      <aside className="right-panel" data-testid="right-panel">
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
            <div className="module-item active">
              <MessageSquare className="w-4 h-4" />
              <span>Chat Engine</span>
            </div>
            <div className="module-item active">
              <Mic className="w-4 h-4" />
              <span>Voice Agent</span>
            </div>
            <div className="module-item active">
              <Eye className="w-4 h-4" />
              <span>Vision Agent</span>
            </div>
            <div className="module-item active">
              <Sparkles className="w-4 h-4" />
              <span>Design Agent</span>
            </div>
          </div>
        </div>
        
        <div className="panel-section capabilities">
          <div className="panel-title">
            <Brain className="w-4 h-4" />
            <span>CAPABILITIES</span>
          </div>
          <div className="capabilities-list">
            <span className="capability-tag">Chat</span>
            <span className="capability-tag">Voice</span>
            <span className="capability-tag">Vision</span>
            <span className="capability-tag">Image Gen</span>
            <span className="capability-tag">Research</span>
            <span className="capability-tag">Analysis</span>
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
      <AuthContext>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </AuthContext>
    </BrowserRouter>
  );
}

export default App;
