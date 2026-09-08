import { useState, useRef, useEffect } from 'react'
import DocumentSidebar from './DocumentSidebar'
import AuthPage from './AuthPage'
import './App.css'

// Base URL of the FastAPI backend
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

function App() {
  const [session, setSession] = useState(() => {
    try { return JSON.parse(localStorage.getItem('rag_session')) } catch { return null }
  })
  // ==========================================
  // State Management
  // ==========================================
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Auto-grow the composer textarea like ChatGPT's input box
  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 200) + 'px'
  }, [input])

  /**
   * Normalize a source entry into { text, filename, page }.
   * Backend may send a plain string (old shape) or an object with
   * filename/page metadata (new shape). We handle both gracefully,
   * checking a few common key names for filename and page.
   */
  const getSourceInfo = (source) => {
    if (typeof source === 'string') {
      return { text: source, filename: null, page: null, url: null }
    }
    const filename = source.filename || source.document || null
    const page = source.page ?? source.page_number ?? null
    const text = source.text || source.content || source.chunk || ''
    // Backend already builds a ready-to-open relative url like
    // /documents/{document_id}/view#page={page} — fall back to
    // constructing it ourselves if only document_id + page are present.
    const url =
      source.url ||
      (source.document_id && page ? `/documents/${source.document_id}/view#page=${page}` : null)
    return { text, filename, page, url }
  }

  /**
   * Opens the source PDF in a new tab, jumped to the right page,
   * using the url the backend already provides per source.
   */
  const openSource = (url) => {
    if (!url) return
    const [path, fragment = ''] = url.split('#')
    const target = `${API_BASE_URL}${path}?access_token=${encodeURIComponent(session.token)}${fragment ? `#${fragment}` : ''}`
    window.open(target, '_blank', 'noopener,noreferrer')
  }

  /**
   * Send query to RAG backend
   */
  const handleSend = async () => {
    if (!input.trim()) return

    const userMessage = { id: Date.now(), text: input, sender: 'user' }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${session.token}` },
        body: JSON.stringify({ query: input })
      })

      const contentType = response.headers.get('content-type') || ''
      const data = contentType.includes('application/json') ? await response.json() : {}
      if (!response.ok) {
        throw new Error(data.detail || 'Unable to get an answer right now. Please try again.')
      }

      const assistantMessage = {
        id: Date.now() + 1,
        text: data.answer || 'No response',
        sender: 'assistant',
        sources: data.sources || []
      }
      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error:', error)
      const errorMessage = {
        id: Date.now() + 1,
        text: error.message || 'Unable to connect. Please try again.',
        sender: 'assistant'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleNewChat = () => {
    setMessages([])
    setInput('')
  }

  const selectSuggestion = (suggestion) => {
    setInput(suggestion)
    textareaRef.current?.focus()
  }

  if (!session) return <AuthPage onAuthenticated={(data) => {
    const next = { token: data.access_token, user: data.user }
    localStorage.setItem('rag_session', JSON.stringify(next)); setSession(next)
  }} />

  const logout = () => { localStorage.removeItem('rag_session'); setSession(null) }
  const isAdmin = session.user.role === 'admin'

  return (
    <div className="app-wrapper">
      {/* Left Sidebar - Document Management */}
      {isAdmin && <DocumentSidebar onNewChat={handleNewChat} token={session.token} />}

      {/* Main Chat Container */}
      <div className="app-container">
        {/* Header */}
        <header className="app-header">
          <span className="header-title">RAG Assistant</span>
          <div className="account-menu"><span>{session.user.name}</span>{isAdmin && <b>ADMIN</b>}<button onClick={logout}>Sign out</button></div>
        </header>

        {/* Messages Container */}
        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="empty-state">
              <div className="empty-cube">
                <svg viewBox="0 0 100 100" width="64" height="64">
                  <polygon points="50,6 90,28 90,72 50,94 10,72 10,28" fill="none" stroke="url(#cubeGradEmpty)" strokeWidth="1.4"/>
                  <polygon points="50,6 90,28 50,50 10,28" fill="none" stroke="url(#cubeGradEmpty)" strokeWidth="1.4"/>
                  <line x1="50" y1="50" x2="50" y2="94" stroke="url(#cubeGradEmpty)" strokeWidth="1.4"/>
                  <defs>
                    <linearGradient id="cubeGradEmpty" x1="0" y1="0" x2="1" y2="1">
                      <stop offset="0%" stopColor="#f0c368"/>
                      <stop offset="100%" stopColor="#b8862f"/>
                    </linearGradient>
                  </defs>
                </svg>
              </div>
              <p className="welcome-kicker">YOUR PRIVATE KNOWLEDGE BASE</p>
              <h2>What would you like to know?</h2>
              <p>Ask a question about your uploaded documents. Every answer includes page-level sources you can open.</p>
              <div className="suggestion-grid">
                {['Summarize the key points', 'What are the main requirements?', 'Find important dates and deadlines'].map(suggestion => (
                  <button key={suggestion} onClick={() => selectSuggestion(suggestion)}>{suggestion}<span>↗</span></button>
                ))}
              </div>
            </div>
          ) : (
            <div className="messages-list">
              {messages.map(msg => (
                <div key={msg.id} className={`message message-${msg.sender}`}>
                  {msg.sender === 'assistant' && (
                    <div className="assistant-avatar">
                      <svg viewBox="0 0 100 100" width="20" height="20">
                        <polygon points="50,6 90,28 90,72 50,94 10,72 10,28" fill="none" stroke="url(#cubeGradMsg)" strokeWidth="4"/>
                        <polygon points="50,6 90,28 50,50 10,28" fill="none" stroke="url(#cubeGradMsg)" strokeWidth="4"/>
                        <line x1="50" y1="50" x2="50" y2="94" stroke="url(#cubeGradMsg)" strokeWidth="4"/>
                        <defs>
                          <linearGradient id="cubeGradMsg" x1="0" y1="0" x2="1" y2="1">
                            <stop offset="0%" stopColor="#f0c368"/>
                            <stop offset="100%" stopColor="#b8862f"/>
                          </linearGradient>
                        </defs>
                      </svg>
                    </div>
                  )}
                  <div className="message-content">
                    <span className="message-label">{msg.sender === 'user' ? 'You' : 'RAG Vault'}</span>
                    <div className="message-text">{msg.text}</div>
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="sources-row">
                        {msg.sources.map((source, idx) => {
                          const { text, filename, page, url } = getSourceInfo(source)
                          const clickable = Boolean(url)
                          return (
                            <button
                              key={idx}
                              className={`source-chip ${clickable ? '' : 'source-chip-disabled'}`}
                              onClick={() => openSource(url)}
                              disabled={!clickable}
                              title={text || filename || `Source ${idx + 1}`}
                              type="button"
                            >
                              <span className="chip-index">{idx + 1}</span>
                              <span className="chip-name">{filename || 'Source'}</span>
                              {page && <span className="chip-page">p.{page}</span>}
                              {clickable && (
                                <svg className="chip-arrow" width="11" height="11" viewBox="0 0 24 24" fill="none">
                                  <path d="M7 17L17 7M17 7H9M17 7V15" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/>
                                </svg>
                              )}
                            </button>
                          )
                        })}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="message message-assistant">
                  <div className="assistant-avatar">
                    <svg viewBox="0 0 100 100" width="20" height="20">
                      <polygon points="50,6 90,28 90,72 50,94 10,72 10,28" fill="none" stroke="url(#cubeGradLoad)" strokeWidth="4"/>
                      <polygon points="50,6 90,28 50,50 10,28" fill="none" stroke="url(#cubeGradLoad)" strokeWidth="4"/>
                      <line x1="50" y1="50" x2="50" y2="94" stroke="url(#cubeGradLoad)" strokeWidth="4"/>
                      <defs>
                        <linearGradient id="cubeGradLoad" x1="0" y1="0" x2="1" y2="1">
                          <stop offset="0%" stopColor="#f0c368"/>
                          <stop offset="100%" stopColor="#b8862f"/>
                        </linearGradient>
                      </defs>
                    </svg>
                  </div>
                  <div className="message-content">
                    <div className="loading-dots">
                      <span></span><span></span><span></span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="input-container">
          <div className="input-wrapper">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question about your documents…"
              className="message-input"
              disabled={loading}
              rows="1"
            />
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="send-button"
              aria-label="Send message"
            >
              {loading ? (
                <span className="send-spinner"></span>
              ) : (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path d="M12 19V5M12 5L5 12M12 5L19 12" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              )}
            </button>
          </div>
          <p className="input-hint">Answers are grounded in your documents. Review cited sources for important decisions.</p>
        </div>
      </div>
    </div>
  )
}

export default App
