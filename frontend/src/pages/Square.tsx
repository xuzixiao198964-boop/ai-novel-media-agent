export default function Square() {
  return (
    <div className="page">
      <h1 className="page-title">作品广场</h1>

      <div className="tabs">
        <div className="tab active">推荐</div>
        <div className="tab">小说</div>
        <div className="tab">视频</div>
        <div className="tab">儿童</div>
      </div>

      <div className="work-grid">
        <div className="work-card">
          <div className="cover">📖</div>
          <div className="body">
            <h3>《剑来》AI续写</h3>
            <p>玄幻 · 长篇 · by 用户A · ⭐4.8</p>
          </div>
        </div>

        <div className="work-card">
          <div className="cover pink">🎬</div>
          <div className="body">
            <h3>AI创业浪潮</h3>
            <p>资讯视频 · 03:20 · by 用户B</p>
          </div>
        </div>

        <div className="work-card">
          <div className="cover cyan">👶</div>
          <div className="body">
            <h3>《森林音乐会》</h3>
            <p>儿童 · 3-6岁 · by 用户C</p>
          </div>
        </div>

        <div className="work-card">
          <div className="cover orange">📖</div>
          <div className="body">
            <h3>《冰封战线》</h3>
            <p>军事 · 中篇 · by 用户D · ⭐4.6</p>
          </div>
        </div>
      </div>
    </div>
  )
}
