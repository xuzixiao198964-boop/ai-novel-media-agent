import './Settings.css'

export default function Settings() {
  return (
    <div className="page">
      <h1 className="page-title">设置</h1>

      <div className="card">
        <h2>个人资料</h2>
        <div className="form-container">
          <label>
            昵称
            <input type="text" defaultValue="AI创作者" />
          </label>
          <label>
            邮箱
            <input type="email" defaultValue="user@example.com" />
          </label>
          <label>
            手机
            <input type="tel" defaultValue="138****1234" />
          </label>
          <button className="btn btn-primary">保存</button>
        </div>
      </div>
    </div>
  )
}
