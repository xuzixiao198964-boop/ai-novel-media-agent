import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'

const Login = () => {
  const navigate = useNavigate()
  const { login, isLoading } = useAuthStore()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    try {
      await login(email, password)
      navigate('/')
    } catch (err: any) {
      setError(err.response?.data?.message || '登录失败，请检查邮箱和密码')
    }
  }

  return (
    <div className="login-container">
      <div className="login-box">
        <h1>AI 创作平台</h1>

        {error && (
          <div style={{
            padding: '12px',
            background: '#fee2e2',
            color: '#dc2626',
            borderRadius: '8px',
            marginBottom: '20px',
            fontSize: '0.9rem'
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>邮箱</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="请输入邮箱"
              required
            />
          </div>

          <div className="form-group">
            <label>密码</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="请输入密码"
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '8px' }}
            disabled={isLoading}
          >
            {isLoading ? '登录中...' : '登录'}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '20px', fontSize: '0.9rem' }}>
          还没有账号？
          <Link to="/register" style={{ color: '#6366f1', marginLeft: '8px' }}>
            立即注册
          </Link>
        </div>
      </div>
    </div>
  )
}

export default Login
