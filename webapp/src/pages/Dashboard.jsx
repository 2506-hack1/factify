// src/pages/Dashboard.jsx
import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'

export default function Dashboard() {
  const [view, setView] = useState('consumer')
  const navigate = useNavigate()

  return (
    <div style={{ maxWidth: '600px', margin: '2rem auto', textAlign: 'center' }}>
      <h2>Dashboard</h2>

      <div style={{ marginBottom: '1.5rem' }}>
        <button
          onClick={() => setView('consumer')}
          style={{
            padding: '0.5rem 1rem',
            marginRight: '1rem',
            backgroundColor: view === 'consumer' ? '#ccc' : '#eee',
          }}
        >
          Consumer
        </button>
        <button
          onClick={() => setView('provider')}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: view === 'provider' ? '#ccc' : '#eee',
          }}
        >
          Provider
        </button>
      </div>

      {view === 'provider' ? (
        <div>
          <p>ようこそ、Provider 用ダッシュボードへ。</p>
          <button
            onClick={() => navigate('/upload')}
            style={{ padding: '0.75rem 1.5rem', marginTop: '1rem' }}
          >
            Upload
          </button>
        </div>
      ) : (
        <div>
          <p>ようこそ、Consumer 用ダッシュボードへ。</p>
          {/* Consumer には Upload ボタンなし */}
        </div>
      )}

      <div style={{ marginTop: '2rem' }}>
        <Link to="/">← Log Out</Link>
      </div>
    </div>
  )
}
