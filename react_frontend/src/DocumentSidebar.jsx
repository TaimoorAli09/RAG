import { useState, useRef, useEffect, useCallback } from 'react'
import './DocumentSidebar.css'

// Base URL of the FastAPI backend
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

function DocumentSidebar({ onNewChat, token }) {
  const authHeaders = { Authorization: `Bearer ${token}` }
  // State management
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState('')
  const [dragOver, setDragOver] = useState(false)
  const [collapsed, setCollapsed] = useState(false)
  const fileInputRef = useRef(null)

  /**
   * Fetch list of all uploaded documents from backend
   */
  const fetchDocuments = useCallback(async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE_URL}/documents/list`, { headers: { Authorization: `Bearer ${token}` } })
      const data = await response.json()
      setDocuments(data.documents || [])
    } catch (error) {
      console.error('Error fetching documents:', error)
    } finally {
      setLoading(false)
    }
  }, [token])

  /**
   * Upload files (single PDF or ZIP containing multiple PDFs)
   * Supports drag-and-drop and file input
   */
  const handleUpload = async (files) => {
    if (files.length === 0) return

    setUploading(true)
    setUploadError('')
    const uploadPromises = []

    for (const file of files) {
      if (!file.name.endsWith('.pdf') && !file.name.endsWith('.zip')) {
        alert(`${file.name} is not a PDF or ZIP file`)
        continue
      }

      const formData = new FormData()
      formData.append('file', file)

      uploadPromises.push((async () => {
        const response = await fetch(`${API_BASE_URL}/documents/upload`, {
          method: 'POST',
          headers: authHeaders,
          body: formData
        })
        const contentType = response.headers.get('content-type') || ''
        const data = contentType.includes('application/json') ? await response.json() : {}
        if (!response.ok) throw new Error(data.detail || `${file.name} could not be uploaded`)
        return data
      })())
    }

    try {
      const results = await Promise.all(uploadPromises)
      await fetchDocuments()
      alert(`${results.length} document${results.length !== 1 ? 's' : ''} uploaded successfully.`)
    } catch (error) {
      console.error('Error during uploads:', error)
      setUploadError(error.message || 'Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  const handleFileInputChange = (e) => {
    const files = Array.from(e.target.files)
    handleUpload(files)
    e.target.value = ''
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragOver(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragOver(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragOver(false)
    const files = Array.from(e.dataTransfer.files)
    handleUpload(files)
  }

  // Opens the raw PDF in a new tab (page 1), using the document's id
  // to match the backend's /documents/{document_id}/view route.
  const openDocument = (doc) => {
    if (!doc?.id) return
    window.open(`${API_BASE_URL}/documents/${doc.id}/view?access_token=${encodeURIComponent(token)}`, '_blank', 'noopener,noreferrer')
  }

  // Fetch once on load; later updates happen after upload, rename, or delete.
  useEffect(() => {
    const initialFetch = window.setTimeout(fetchDocuments, 0)
    return () => window.clearTimeout(initialFetch)
  }, [fetchDocuments])

  const renameDocument = async (doc) => {
    const filename = window.prompt('New filename', doc.filename)
    if (!filename?.trim()) return
    await fetch(`${API_BASE_URL}/documents/${doc.id}?filename=${encodeURIComponent(filename)}`, { method: 'PATCH', headers: authHeaders })
    fetchDocuments()
  }
  const deleteDocument = async (doc) => {
    if (!window.confirm(`Delete ${doc.filename}? This cannot be undone.`)) return
    await fetch(`${API_BASE_URL}/documents/${doc.id}`, { method: 'DELETE', headers: authHeaders })
    fetchDocuments()
  }

  // Collapsed rail — just a floating button to reopen, like ChatGPT
  if (collapsed) {
    return (
      <button
        className="sidebar-expand-btn"
        onClick={() => setCollapsed(false)}
        title="Open sidebar"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
          <rect x="3" y="4" width="18" height="16" rx="2" stroke="currentColor" strokeWidth="1.6"/>
          <line x1="9" y1="4" x2="9" y2="20" stroke="currentColor" strokeWidth="1.6"/>
        </svg>
      </button>
    )
  }

  return (
    <div className="document-sidebar">
      {/* Header */}
      <div className="sidebar-header">
        <span className="sidebar-logo">
          <svg viewBox="0 0 100 100" width="16" height="16">
            <polygon points="50,6 90,28 90,72 50,94 10,72 10,28" fill="none" stroke="url(#sbCubeGrad)" strokeWidth="6"/>
            <polygon points="50,6 90,28 50,50 10,28" fill="none" stroke="url(#sbCubeGrad)" strokeWidth="6"/>
            <line x1="50" y1="50" x2="50" y2="94" stroke="url(#sbCubeGrad)" strokeWidth="6"/>
            <defs>
              <linearGradient id="sbCubeGrad" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor="#f0c368"/>
                <stop offset="100%" stopColor="#b8862f"/>
              </linearGradient>
            </defs>
          </svg>
          RAG
        </span>
        <button
          className="icon-btn"
          onClick={() => setCollapsed(true)}
          title="Close sidebar"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <rect x="3" y="4" width="18" height="16" rx="2" stroke="currentColor" strokeWidth="1.6"/>
            <line x1="9" y1="4" x2="9" y2="20" stroke="currentColor" strokeWidth="1.6"/>
          </svg>
        </button>
      </div>

      {/* New Chat */}
      <button className="new-chat-btn" onClick={onNewChat}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
          <path d="M12 5V19M5 12H19" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
        </svg>
        New chat
      </button>

      {/* Upload Area */}
      <div
        className={`upload-area ${dragOver ? 'drag-over' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.zip"
          onChange={handleFileInputChange}
          disabled={uploading}
          style={{ display: 'none' }}
        />
        <button
          className="upload-btn"
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
        >
          {uploading ? 'Uploading...' : '+ Upload files'}
        </button>
        <p className="upload-hint">
          {dragOver ? 'Drop files here' : 'PDF or ZIP, drag & drop'}
        </p>
        {uploadError && <p className="upload-error">{uploadError}</p>}
      </div>

      {/* Documents List */}
      <div className="documents-list">
        {loading && documents.length === 0 ? (
          <div className="empty-state">
            <div className="spinner"></div>
            <p>Loading documents...</p>
          </div>
        ) : documents.length === 0 ? (
          <div className="empty-state">
            <p>No documents yet</p>
            <small>Upload a PDF or ZIP to get started</small>
          </div>
        ) : (
          <>
            <p className="documents-count">
              {documents.length} document{documents.length !== 1 ? 's' : ''}
            </p>
            {documents.map(doc => (
              <div
                key={doc.id}
                className="document-item"
                onClick={() => openDocument(doc)}
                title={`Open ${doc.filename}`}
              >
                <div className="doc-icon">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <path d="M6 2H14L20 8V22H6V2Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round"/>
                    <path d="M14 2V8H20" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round"/>
                  </svg>
                </div>
                <div className="doc-info">
                  <div className="doc-name" title={doc.filename}>
                    {doc.filename}
                  </div>
                  <div className="doc-meta">
                    {doc.chunks} chunks
                  </div>
                </div>
                <svg className="doc-open-arrow" width="12" height="12" viewBox="0 0 24 24" fill="none">
                  <path d="M7 17L17 7M17 7H9M17 7V15" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                <div className="doc-actions" onClick={(event) => event.stopPropagation()}><button onClick={() => renameDocument(doc)} title="Rename">✎</button><button onClick={() => deleteDocument(doc)} title="Delete">×</button></div>
              </div>
            ))}
          </>
        )}
      </div>

      {/* Footer Stats */}
      {documents.length > 0 && (
        <div className="sidebar-footer">
          <div className="stat">
            <span className="stat-label">Documents</span>
            <span className="stat-value">{documents.length}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Chunks</span>
            <span className="stat-value">
              {documents.reduce((sum, doc) => sum + (doc.chunks || 0), 0)}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}

export default DocumentSidebar
