import './Videos.css'

export default function Videos() {
  return (
    <div className="page">
      <h1 className="page-title">视频作品</h1>

      <div className="tabs">
        <div className="tab active">全部</div>
        <div className="tab">小说类</div>
        <div className="tab">资讯类</div>
      </div>

      <div className="card">
        <h2>📁 龙族传说 (小说视频 · 12集)</h2>
        <div className="video-grid">
          <div className="video-item">
            <div className="video-thumb">▶</div>
            <p>第1集 03:25</p>
          </div>
          <div className="video-item">
            <div className="video-thumb">▶</div>
            <p>第2集 04:10</p>
          </div>
          <div className="video-item">
            <div className="video-thumb">▶</div>
            <p>第3集 03:50</p>
          </div>
          <div className="video-item more">+9 集</div>
        </div>
        <div className="video-actions">
          <button className="btn btn-outline">全部下载</button>
          <button className="btn btn-primary">发布抖音</button>
          <button className="btn btn-outline">发布小红书</button>
        </div>
      </div>

      <div className="card">
        <h2>🎬 全球AI峰会速览 (资讯视频)</h2>
        <div className="video-detail">
          <div className="video-thumb-large">▶</div>
          <div>
            <p className="video-meta">时长 02:30 · 资讯类 · 双语</p>
            <div className="video-actions">
              <button className="btn btn-outline">下载</button>
              <button className="btn btn-primary">发布抖音</button>
              <button className="btn btn-outline">发布广场</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
