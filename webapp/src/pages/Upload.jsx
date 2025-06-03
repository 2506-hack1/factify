import { useState } from 'react'
import { Link } from 'react-router-dom'

export default function Upload() {
  const [file, setFile] = useState(null)
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    // ここに「ファイルアップロード＋タイトル/説明登録」のロジックを追加
    alert('アップロード処理をここに実装してください')
  }

  return (
    <div style={{ maxWidth: '500px', margin: '2rem auto' }}>
      <h2 style={{ textAlign: 'center' }}>Upload PDF</h2>

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '1rem' }}>
          <label>
            PDF File:
            <input
              type="file"
              accept=".pdf"
              onChange={e => {
                if (e.target.files && e.target.files[0]) {
                  setFile(e.target.files[0])
                }
              }}
              required
              style={{ display: 'block', marginTop: '0.5rem' }}
            />
          </label>
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <label>
            Title:
            <input
              type="text"
              value={title}
              onChange={e => setTitle(e.target.value)}
              required
              style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
            />
          </label>
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <label>
            Description:
            <textarea
              value={description}
              onChange={e => setDescription(e.target.value)}
              required
              style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem', minHeight: '100px' }}
            />
          </label>
        </div>

        <button type="submit" style={{ width: '100%', padding: '0.75rem' }}>
          Send
        </button>
      </form>

      <div style={{ marginTop: '1rem', textAlign: 'center' }}>
        <Link to="/dashboard">← Back to Dashboard</Link>
      </div>
    </div>
  )
}