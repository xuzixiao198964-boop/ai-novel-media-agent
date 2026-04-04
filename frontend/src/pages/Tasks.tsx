import './Tasks.css'

export default function Tasks() {
  return (
    <div className="page">
      <h1 className="page-title">我的任务</h1>

      <div className="card">
        <div className="task-list">
          <div className="task-item">
            <div className="status running"></div>
            <div className="info">
              <h4>《龙族传说》</h4>
              <p>玄幻·长篇 | 写作中 第12/30章 | 预估剩余45min</p>
              <div className="progress-bar">
                <div className="fill" style={{ width: '65%' }}></div>
              </div>
            </div>
            <span className="badge badge-green">运行中</span>
          </div>

          <div className="task-item">
            <div className="status queued"></div>
            <div className="info">
              <h4>《霸总的甜蜜陷阱》</h4>
              <p>霸总·短篇 | 排队第5位 | 预估等待25min</p>
            </div>
            <span className="badge badge-yellow">排队中</span>
          </div>

          <div className="task-item">
            <div className="status done"></div>
            <div className="info">
              <h4>《星际迷途》</h4>
              <p>科幻·中篇 | 已完成 | 消耗¥6.20</p>
              <div className="progress-bar">
                <div className="fill" style={{ width: '100%' }}></div>
              </div>
            </div>
            <span className="badge badge-blue">已完成</span>
          </div>
        </div>
      </div>

      <div className="card detail-card">
        <h2 style={{ color: '#16a34a' }}>📋 任务详情 — 《龙族传说》</h2>
        <div className="detail-grid">
          <div>
            <span className="detail-label">类型</span><br />
            <strong>玄幻 · 长篇</strong>
          </div>
          <div>
            <span className="detail-label">排队</span><br />
            <strong>无（运行中）</strong>
          </div>
          <div>
            <span className="detail-label">预估剩余</span><br />
            <strong>45 分钟</strong>
          </div>
        </div>

        <table className="agent-table">
          <thead>
            <tr>
              <th>Agent</th>
              <th>状态</th>
              <th>耗时</th>
              <th>备注</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>✅ 趋势分析</td>
              <td><span className="badge badge-blue">完成</span></td>
              <td>3m12s</td>
              <td></td>
            </tr>
            <tr>
              <td>✅ 风格解析</td>
              <td><span className="badge badge-blue">完成</span></td>
              <td>2m45s</td>
              <td></td>
            </tr>
            <tr>
              <td>✅ 策划大纲</td>
              <td><span className="badge badge-blue">完成</span></td>
              <td>5m20s</td>
              <td>引用：麦基冲突理论 + 黄金三章</td>
            </tr>
            <tr>
              <td>🔄 章节写作</td>
              <td><span className="badge badge-green">进行中</span></td>
              <td>-</td>
              <td>第12/30章</td>
            </tr>
            <tr>
              <td>○ 润色</td>
              <td><span className="badge badge-yellow">等待</span></td>
              <td>-</td>
              <td></td>
            </tr>
            <tr>
              <td>○ 审计</td>
              <td><span className="badge badge-yellow">等待</span></td>
              <td>-</td>
              <td></td>
            </tr>
            <tr>
              <td>○ 冲突校验</td>
              <td><span className="badge badge-yellow">等待</span></td>
              <td>-</td>
              <td></td>
            </tr>
            <tr>
              <td>○ 修订</td>
              <td><span className="badge badge-yellow">等待</span></td>
              <td>-</td>
              <td></td>
            </tr>
          </tbody>
        </table>

        <p className="estimate-text">预估消耗：¥12.50 | 当前余额：¥88.30</p>
      </div>
    </div>
  )
}
