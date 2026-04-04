import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { getRunningTasks } from '@/api/tasks'
import { getStats } from '@/api/stats'
import { Task, Stats } from '@/types'
import { formatCurrency } from '@/utils/format'

const Dashboard = () => {
  const { user } = useAuthStore()
  const [stats, setStats] = useState<Stats | null>(null)
  const [runningTasks, setRunningTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [statsData, tasksData] = await Promise.all([
        getStats(),
        getRunningTasks()
      ])
      setStats(statsData)
      setRunningTasks(tasksData)
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div>
        <div className="topbar">
          <h1>仪表盘</h1>
        </div>
        <div style={{ textAlign: 'center', padding: '40px' }}>加载中...</div>
      </div>
    )
  }

  return (
    <div>
      <div className="topbar">
        <h1>仪表盘</h1>
        <div className="user-info">
          <div className="balance">
            余额: <span>{formatCurrency(user?.balance || 0)}</span>
          </div>
          <div style={{
            width: '36px',
            height: '36px',
            background: '#6366f1',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            fontSize: '0.9rem'
          }}>
            {user?.username?.charAt(0).toUpperCase() || 'U'}
          </div>
        </div>
      </div>

      {/* 统计卡片 */}
      <div className="stats">
        <div className="stat-card">
          <div className="label">进行中任务</div>
          <div className="value">{stats?.runningTasks || 0}</div>
          <div className="sub">{stats?.queuedTasks || 0} 排队中</div>
        </div>
        <div className="stat-card">
          <div className="label">已完成作品</div>
          <div className="value">{stats?.completedWorks || 0}</div>
          <div className="sub">{stats?.novels || 0} 小说 · {stats?.videos || 0} 视频</div>
        </div>
        <div className="stat-card">
          <div className="label">本月消费</div>
          <div className="value">{formatCurrency(stats?.monthlySpending || 0)}</div>
          <div className="sub">
            小说{formatCurrency(stats?.novelSpending || 0)} · 视频{formatCurrency(stats?.videoSpending || 0)}
          </div>
        </div>
        <div className="stat-card">
          <div className="label">当前套餐</div>
          <div className="value" style={{ fontSize: '1.2rem' }}>
            {stats?.currentPackage || '基础版'}
          </div>
          <div className="sub">小说+视频</div>
        </div>
      </div>

      {/* 进行中的任务 */}
      <div className="card">
        <h2>进行中的任务</h2>
        {runningTasks.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#64748b' }}>
            暂无进行中的任务
            <br />
            <Link to="/create" className="btn btn-primary" style={{ marginTop: '16px' }}>
              创建新任务
            </Link>
          </div>
        ) : (
          <div className="task-list">
            {runningTasks.map((task) => (
              <div key={task.id} className="task-item">
                <div className={`status ${task.status === 'running' ? 'running' : 'queued'}`}></div>
                <div className="info">
                  <h4>{task.title}</h4>
                  <p>
                    {task.description} ·
                    {task.status === 'running'
                      ? ` 预估剩余 ${task.estimatedTime || 0} 分钟`
                      : ` 排队位置：第 ${task.queuePosition || 0}`
                    }
                  </p>
                  {task.progress > 0 && (
                    <div className="progress-bar">
                      <div className="fill" style={{ width: `${task.progress}%` }}></div>
                    </div>
                  )}
                </div>
                <span className={`badge ${task.status === 'running' ? 'badge-green' : 'badge-yellow'}`}>
                  {task.status === 'running' ? '生成中' : '排队中'}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard
