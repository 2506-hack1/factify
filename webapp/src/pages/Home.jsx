import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div style={{ textAlign: 'center', marginTop: '5rem' }}>
      <h1>factify</h1>
      <div style={{ marginTop: '2rem' }}>
        {/* Sign In なら createAccount=false を渡す */}
        <Link to="/signup?createAccount=false">
          <button style={{ marginRight: '1rem', padding: '0.5rem 1rem' }}>
            Sign In
          </button>
        </Link>

        {/* Create Account なら createAccount=true を渡す */}
        <Link to="/signup?createAccount=true">
          <button style={{ padding: '0.5rem 1rem' }}>
            Sign Up
          </button>
        </Link>
      </div>
    </div>
  )
}
