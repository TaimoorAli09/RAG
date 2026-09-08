import { useState } from 'react'
import './AuthPage.css'

// Always use the same-origin proxy. Vite forwards /api in development and
// Nginx forwards it to the API container in Docker/AWS.
const API = import.meta.env.VITE_API_URL || '/api'

export default function AuthPage({ onAuthenticated }) {
  const [mode, setMode] = useState('login')
  const [form, setForm] = useState({ full_name: '', email: '', password: '', code: '' })
  const [pendingEmail, setPendingEmail] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const verifyMode = mode === 'verify'

  const update = (event) => setForm({ ...form, [event.target.name]: event.target.value })
  const submit = async (event) => {
    event.preventDefault()
    setError(''); setLoading(true)
    const endpoint = verifyMode ? '/auth/verify-otp' : mode === 'login' ? '/auth/login' : '/auth/signup'
    const body = verifyMode ? { email: pendingEmail, code: form.code } : mode === 'login'
      ? { email: form.email, password: form.password }
      : { full_name: form.full_name, email: form.email, password: form.password }
    try {
      const response = await fetch(`${API}${endpoint}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
      const contentType = response.headers.get('content-type') || ''
      const data = contentType.includes('application/json') ? await response.json() : { detail: 'Server returned an unexpected response. Check the web container and API route.' }
      if (!response.ok) {
        if (response.status === 403 && mode === 'login') { setPendingEmail(form.email); setMode('verify') }
        const message = Array.isArray(data.detail) ? data.detail.map(item => item.msg).join('. ') : data.detail
        throw new Error(message || 'Unable to continue')
      }
      if (mode === 'signup') { setPendingEmail(form.email); setMode('verify'); return }
      onAuthenticated(data)
    } catch (err) { setError(err.message) } finally { setLoading(false) }
  }
  const switchMode = () => { setError(''); setMode(mode === 'login' ? 'signup' : 'login') }

  return <main className="auth-shell">
    <div className="orb orb-one" /><div className="orb orb-two" />
    <section className="auth-panel">
      <div className="brand-mark">◈</div>
      <p className="eyebrow">PRIVATE KNOWLEDGE, REFINED</p>
      <h1>{verifyMode ? 'Verify your inbox' : mode === 'login' ? 'Welcome back' : 'Create your vault'}</h1>
      <p className="auth-subtitle">{verifyMode ? `We sent a 6-digit code to ${pendingEmail}.` : 'Your documents, transformed into answers.'}</p>
      <form onSubmit={submit}>
        {mode === 'signup' && <label>Full name<input name="full_name" value={form.full_name} onChange={update} required minLength="2" placeholder="Your name" /></label>}
        {!verifyMode && <label>Email<input type="email" name="email" value={form.email} onChange={update} required placeholder="you@company.com" /></label>}
        {!verifyMode && <label>Password<input type="password" name="password" value={form.password} onChange={update} required minLength="8" placeholder="At least 8 characters" /></label>}
        {verifyMode && <label>Verification code<input className="otp-input" inputMode="numeric" name="code" value={form.code} onChange={update} required pattern="[0-9]{6}" maxLength="6" placeholder="000000" /></label>}
        {error && <p className="auth-error">{error}</p>}
        <button className="auth-submit" disabled={loading}>{loading ? 'Please wait…' : verifyMode ? 'Verify & enter' : mode === 'login' ? 'Sign in' : 'Send verification code'}</button>
      </form>
      {!verifyMode && <button className="auth-switch" onClick={switchMode}>{mode === 'login' ? 'New here? Create an account' : 'Already have an account? Sign in'}</button>}
    </section>
  </main>
}
