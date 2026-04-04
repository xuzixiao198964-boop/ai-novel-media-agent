import './Novels.css'

export default function Novels() {
  return (
    <div className="page">
      <h1 className="page-title">小说作品</h1>

      <div className="tabs">
        <div className="tab active">全部</div>
        <div className="tab">儿童故事</div>
        <div className="tab">男频</div>
        <div className="tab">女频</div>
      </div>

      <div className="work-grid">
        <div className="work-card">
          <div className="cover">📖</div>
          <div className="body">
            <h3>《龙族传说》</h3>
            <p>玄幻 · 长篇 · 32万字 · ⭐ 4.5</p>
            <div className="actions">
              <a href="#">下载</a>
              <a href="#">发布广场</a>
              <a href="#">发布番茄</a>
              <a href="#" className="danger">删除</a>
            </div>
          </div>
        </div>

        <div className="work-card">
          <div className="cover pink">💕</div>
          <div className="body">
            <h3>《霸总的秘密》</h3>
            <p>霸总 · 短篇 · 2.8万字 · ⭐ 4.2</p>
            <div className="actions">
              <a href="#">下载</a>
              <a href="#" className="published">已发布 ✓</a>
              <a href="#" className="danger">删除</a>
            </div>
          </div>
        </div>

        <div className="work-card">
          <div className="cover cyan">👶</div>
          <div className="body">
            <h3>《小兔子的冒险》</h3>
            <p>儿童 · 3-6岁 · 微小说 · 3千字</p>
            <div className="actions">
              <a href="#">下载</a>
              <a href="#">发布广场</a>
              <a href="#" className="danger">删除</a>
            </div>
          </div>
        </div>

        <div className="work-card">
          <div className="cover orange">🔍</div>
          <div className="body">
            <h3>《迷雾之城》</h3>
            <p>悬疑 · 中篇 · 8万字 · ⭐ 4.7</p>
            <div className="actions">
              <a href="#">下载</a>
              <a href="#">发布广场</a>
              <a href="#" className="danger">删除</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
