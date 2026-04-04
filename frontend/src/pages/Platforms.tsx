import './Platforms.css'

export default function Platforms() {
  return (
    <div className="page">
      <h1 className="page-title">平台账号绑定</h1>

      <div className="card">
        <div className="platform-list">
          <div className="platform-item">
            <div className="platform-info">
              <span className="platform-icon">🎵</span>
              <div>
                <strong>抖音</strong>
                <br />
                <span className="platform-desc">用于视频自动发布</span>
              </div>
            </div>
            <button className="btn btn-primary">绑定账号</button>
          </div>

          <div className="platform-item">
            <div className="platform-info">
              <span className="platform-icon">📕</span>
              <div>
                <strong>小红书</strong>
                <br />
                <span className="platform-desc">用于视频/图文发布</span>
              </div>
            </div>
            <button className="btn btn-primary">绑定账号</button>
          </div>

          <div className="platform-item bound">
            <div className="platform-info">
              <span className="platform-icon">🍅</span>
              <div>
                <strong>番茄小说</strong> <span className="badge badge-green">已绑定</span>
                <br />
                <span className="platform-desc">作者：AI创作者001</span>
              </div>
            </div>
            <button className="btn btn-outline">解除绑定</button>
          </div>

          <div className="platform-item">
            <div className="platform-info">
              <span className="platform-icon">📚</span>
              <div>
                <strong>起点</strong>
                <br />
                <span className="platform-desc">用于小说发布</span>
              </div>
            </div>
            <button className="btn btn-primary">绑定账号</button>
          </div>
        </div>
      </div>
    </div>
  )
}
