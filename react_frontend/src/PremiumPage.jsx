import { useState } from 'react'
import './PremiumPage.css'

function PremiumPage() {
  const [showSource, setShowSource] = useState(false)

  const sourceCode = `import { useState } from 'react'
import './PremiumPage.css'

function PremiumPage() {
  const [showSource, setShowSource] = useState(false)

  return (
    <div className="premium-page">
      {/* Premium Header */}
      <div className="premium-header">
        <div className="header-content">
          <h1>RAG System Dashboard</h1>
          <p className="subtitle">Retrieval-Augmented Generation Evaluation</p>
        </div>
      </div>

      {/* Stats Section */}
      <div className="stats-container">
        <div className="stat-card">
          <div className="stat-number">100%</div>
          <div className="stat-label">Retrieval Accuracy</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">11/11</div>
          <div className="stat-label">Queries Processed</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">5.8s</div>
          <div className="stat-label">Avg Latency</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">∞</div>
          <div className="stat-label">Scalability</div>
        </div>
      </div>

      {/* Features Section */}
      <div className="features-section">
        <h2>Core Features</h2>
        <div className="features-grid">
          <div className="feature-box">
            <div className="feature-icon">🔍</div>
            <h3>Hybrid Search</h3>
            <p>BM25 + Semantic + RRF + Reranking</p>
          </div>
          <div className="feature-box">
            <div className="feature-icon">🤖</div>
            <h3>Smart Generation</h3>
            <p>Context-aware answer generation</p>
          </div>
          <div className="feature-box">
            <div className="feature-icon">⚡</div>
            <h3>Fast & Efficient</h3>
            <p>PostgreSQL with pgvector</p>
          </div>
          <div className="feature-box">
            <div className="feature-icon">📊</div>
            <h3>Real-time Metrics</h3>
            <p>Live performance tracking</p>
          </div>
        </div>
      </div>

      {/* Source Code Section */}
      <div className="source-section">
        <div className="source-header">
          <h3>Page Source Code</h3>
          <button 
            className="toggle-btn"
            onClick={() => setShowSource(!showSource)}
          >
            {showSource ? '👁️ Hide' : '👁️ View'} Source
          </button>
        </div>
        {showSource && (
          <div className="source-code">
            <pre>{sourceCode}</pre>
          </div>
        )}
      </div>

      {/* Tech Stack */}
      <div className="tech-stack">
        <h2>Technology Stack</h2>
        <div className="tech-grid">
          <span className="tech-badge">React 18</span>
          <span className="tech-badge">FastAPI</span>
          <span className="tech-badge">PostgreSQL</span>
          <span className="tech-badge">Ollama</span>
          <span className="tech-badge">Vector DB</span>
          <span className="tech-badge">Python 3.12</span>
        </div>
      </div>
    </div>
  )
}

export default PremiumPage`

  return (
    <div className="premium-page">
      {/* Premium Header */}
      <div className="premium-header">
        <div className="header-content">
          <h1>RAG System Dashboard</h1>
          <p className="subtitle">Retrieval-Augmented Generation Evaluation</p>
        </div>
      </div>

      {/* Stats Section */}
      <div className="stats-container">
        <div className="stat-card">
          <div className="stat-number">100%</div>
          <div className="stat-label">Retrieval Accuracy</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">11/11</div>
          <div className="stat-label">Queries Processed</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">5.8s</div>
          <div className="stat-label">Avg Latency</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">∞</div>
          <div className="stat-label">Scalability</div>
        </div>
      </div>

      {/* Features Section */}
      <div className="features-section">
        <h2>Core Features</h2>
        <div className="features-grid">
          <div className="feature-box">
            <div className="feature-icon">🔍</div>
            <h3>Hybrid Search</h3>
            <p>BM25 + Semantic + RRF + Reranking</p>
          </div>
          <div className="feature-box">
            <div className="feature-icon">🤖</div>
            <h3>Smart Generation</h3>
            <p>Context-aware answer generation</p>
          </div>
          <div className="feature-box">
            <div className="feature-icon">⚡</div>
            <h3>Fast & Efficient</h3>
            <p>PostgreSQL with pgvector</p>
          </div>
          <div className="feature-box">
            <div className="feature-icon">📊</div>
            <h3>Real-time Metrics</h3>
            <p>Live performance tracking</p>
          </div>
        </div>
      </div>

      {/* Source Code Section */}
      <div className="source-section">
        <div className="source-header">
          <h3>Page Source Code</h3>
          <button 
            className="toggle-btn"
            onClick={() => setShowSource(!showSource)}
          >
            {showSource ? '👁️ Hide' : '👁️ View'} Source
          </button>
        </div>
        {showSource && (
          <div className="source-code">
            <pre>{sourceCode}</pre>
          </div>
        )}
      </div>

      {/* Tech Stack */}
      <div className="tech-stack">
        <h2>Technology Stack</h2>
        <div className="tech-grid">
          <span className="tech-badge">React 18</span>
          <span className="tech-badge">FastAPI</span>
          <span className="tech-badge">PostgreSQL</span>
          <span className="tech-badge">Ollama</span>
          <span className="tech-badge">Vector DB</span>
          <span className="tech-badge">Python 3.12</span>
        </div>
      </div>
    </div>
  )
}

export default PremiumPage
