import './Package.css'

export default function Package() {
  return (
    <div className="page">
      <h1 className="page-title">套餐管理</h1>

      <div className="package-grid">
        <div className="package-card">
          <h3>基础版</h3>
          <div className="price">¥0.05<span>/千字</span></div>
          <p className="desc">纯小说</p>
          <button className="btn btn-outline">切换</button>
        </div>

        <div className="package-card current">
          <h3>进阶版 <span className="badge badge-blue">当前</span></h3>
          <div className="price">¥0.08+<span>¥0.15/秒</span></div>
          <p className="desc">小说+视频</p>
          <button className="btn btn-primary" disabled>当前套餐</button>
        </div>

        <div className="package-card">
          <h3>专业版</h3>
          <div className="price">¥0.10+<span>¥0.20/秒</span></div>
          <p className="desc">全功能+发布</p>
          <button className="btn btn-outline">升级</button>
        </div>

        <div className="package-card">
          <h3>企业版</h3>
          <div className="price">定制</div>
          <p className="desc">API对接</p>
          <button className="btn btn-outline">联系我们</button>
        </div>
      </div>
    </div>
  )
}
