import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'

import { FiEye, FiEyeOff } from 'react-icons/fi'

export default function Signup() {
    const location = useLocation()
    const navigate = useNavigate()

    // URL のクエリパラメータから createAccountParam を取得（true/false）
    const searchParams = new URLSearchParams(location.search)
    const createAccountParam = searchParams.get('createAccount') === 'true'

    // フォームの入力状態
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')

    // パスワードの見える/見えないの制御
    const [passwordVisible, setPasswordVisible] = useState(false)
    const [confirmVisible, setConfirmVisible] = useState(false)

    const handleSubmit = (e) => {
        e.preventDefault()

        if (createAccountParam && password !== confirmPassword) {
            alert('パスワードと確認用パスワードが一致しません')
            return
        }

        if (createAccountParam) {
            alert('アカウントを作成しました。ダッシュボードへ移動します')
        } else {
            alert('サインインしました。ダッシュボードへ移動します')
        }

        navigate('/dashboard')
    }

    return (
        <div style={{ maxWidth: '700px', margin: '2rem auto', textAlign: 'center' }}>
            <h2 style={{ marginBottom: '1rem' }}>
                {createAccountParam ? 'Create Your Account' : 'Sign In'}
            </h2>
            <div
                style={{
                    border: '1px solid #ccc',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                    borderRadius: '4px',
                    overflow: 'hidden',
                    width: '410px',
                    margin: '0 auto',
                }}
            >
                {/* Sign In / Create Account のタブ切替ボタン */}
                <div style={{ display: 'flex', borderBottom: '1px solid #eee' }}>
                    {/* Sign In ボタン */}
                    <button
                        style={{
                            flex: 1,
                            padding: '0.75rem',
                            border: 'none',
                            backgroundColor: createAccountParam ? '#f0f0f0' : '#047e95',
                            color: createAccountParam ? 'black' : 'white',
                            cursor: createAccountParam ? 'not-allowed' : 'pointer',
                            fontWeight: createAccountParam ? 'normal' : 'bold',
                        }}
                        disabled={createAccountParam}
                        onClick={() => {
                            if (!createAccountParam) {
                                navigate('/signup?createAccount=false')
                            }
                        }}
                    >
                        Sign In
                    </button>

                    {/* Create Account ボタン */}
                    <button
                        style={{
                            flex: 1,
                            padding: '0.75rem',
                            border: 'none',
                            backgroundColor: createAccountParam ? '#047e95' : '#f0f0f0',
                            color: createAccountParam ? 'white' : 'black',
                            cursor: createAccountParam ? 'pointer' : 'not-allowed',
                            fontWeight: createAccountParam ? 'bold' : 'normal',
                        }}
                        disabled={!createAccountParam}
                        onClick={() => {
                            if (createAccountParam) {
                                navigate('/signup?createAccount=true')
                            }
                        }}
                    >
                        Create Account
                    </button>
                </div>

                {/* フォーム本体 */}
                <form onSubmit={handleSubmit} style={{ padding: '1rem', textAlign: 'left' }}>
                    {/* Email フィールド */}
                    <div style={{ marginBottom: '1rem' }}>
                        <label
                            style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}
                        >
                            Email:
                        </label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            style={{
                                width: '100%',
                                boxSizing: 'border-box',
                                padding: '0.5rem',
                                border: '1px solid #ddd',
                                borderRadius: '4px',
                            }}
                        />
                    </div>

                    {/* Password フィールド + 目アイコン */}
                    <div style={{ marginBottom: '1rem', position: 'relative' }}>
                        <label
                            style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}
                        >
                            Password:
                        </label>
                        <input
                            type={passwordVisible ? 'text' : 'password'}
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            style={{
                                width: '100%',
                                boxSizing: 'border-box',
                                padding: '0.5rem 2.5rem 0.5rem 0.5rem', // 右側にアイコンスペース
                                border: '1px solid #ddd',
                                borderRadius: '4px',
                            }}
                        />
                        {/* 目アイコンボタン */}
                        <button
                            type="button"
                            onClick={() => setPasswordVisible((prev) => !prev)}
                            style={{
                                position: 'absolute',
                                top: '76%',
                                right: '0.75rem',
                                transform: 'translateY(-50%)',
                                background: 'none',
                                border: 'none',
                                cursor: 'pointer',
                                padding: 0,
                                lineHeight: 1,
                                color: '#555',
                                fontSize: '1.25rem', // アイコンサイズ調整
                            }}
                        >
                            {passwordVisible ? <FiEyeOff /> : <FiEye />}
                        </button>
                    </div>

                    {/* Confirm Password フィールド + 目アイコン（createAccountParam が true のときのみ表示） */}
                    {createAccountParam && (
                        <div style={{ marginBottom: '1rem', position: 'relative' }}>
                            <label
                                style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}
                            >
                                Confirm Password:
                            </label>
                            <input
                                type={confirmVisible ? 'text' : 'password'}
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                required
                                style={{
                                    width: '100%',
                                    boxSizing: 'border-box',
                                    padding: '0.5rem 2.5rem 0.5rem 0.5rem',
                                    border: '1px solid #ddd',
                                    borderRadius: '4px',
                                }}
                            />
                            {/* Confirm 用 目アイコン */}
                            <button
                                type="button"
                                onClick={() => setConfirmVisible((prev) => !prev)}
                                style={{
                                    position: 'absolute',
                                    top: '76%',
                                    right: '0.75rem',
                                    transform: 'translateY(-50%)',
                                    background: 'none',
                                    border: 'none',
                                    cursor: 'pointer',
                                    padding: 0,
                                    lineHeight: 1,
                                    color: '#555',
                                    fontSize: '1.25rem',
                                }}
                            >
                                {confirmVisible ? <FiEyeOff /> : <FiEye />}
                            </button>
                        </div>
                    )}

                    {/* 送信ボタン */}
                    <button
                        type="submit"
                        style={{
                            width: '100%',
                            boxSizing: 'border-box',
                            padding: '0.75rem',
                            marginTop: '0.5rem',
                            backgroundColor: '#047e95',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            fontSize: '1rem',
                            fontWeight: 'bold',
                            transition: 'background-color 0.3s ease',
                        }}
                    >
                        {createAccountParam ? 'Create Account' : 'Sign In'}
                    </button>
                </form>
            </div>

            <div style={{ marginTop: '1.5rem' }}>
                <Link to="/" style={{ color: '#007bff', textDecoration: 'none' }}>
                    ← Back to Home
                </Link>
            </div>
        </div>
    )
}
