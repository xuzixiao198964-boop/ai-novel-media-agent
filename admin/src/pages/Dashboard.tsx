import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { dashboardApi } from '../api'

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null)
  const [incomeTrend, setIncomeTrend] = useState<any[]>([])
  const [recentUsers, setRecentUsers] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [statsData, trendData, usersData] = await Promise.all([
        dashboardApi.getStats(),
        dashboardApi.getIncomeTrend(30),
        dashboardApi.getRecentUsers(5),
      ]) as unknown as [any, any[], any[]]
      setStats(statsData)
      setIncomeTrend(trendData)
      setRecentUsers(usersData)
    } catch (error) {
      console.error('加载数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-12">加载中...</div>
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">数据概览</h1>

      {/* 统计卡片 */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-xl p-5 border border-gray-200">
          <div className="text-xs text-gray-500 mb-1">用户总数</div>
          <div className="text-3xl font-bold">{stats?.total_users || 0}</div>
          <div className="text-xs text-green-600 mt-1">
            +{stats?.today_new_users || 0} 今日注册
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 border border-gray-200">
          <div className="text-xs text-gray-500 mb-1">活跃任务</div>
          <div className="text-3xl font-bold">{stats?.active_tasks || 0}</div>
          <div className="text-xs text-yellow-600 mt-1">
            排队: {stats?.queued_tasks || 0}
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 border border-gray-200">
          <div className="text-xs text-gray-500 mb-1">今日收入</div>
          <div className="text-3xl font-bold text-green-600">
            ¥{stats?.today_income?.toFixed(2) || '0.00'}
          </div>
          <div className="text-xs text-green-600 mt-1">
            {stats?.income_change > 0 ? '+' : ''}
            {stats?.income_change?.toFixed(1) || 0}% 较昨日
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 border border-gray-200">
          <div className="text-xs text-gray-500 mb-1">作品总数</div>
          <div className="text-3xl font-bold">
            {(stats?.total_novels || 0) + (stats?.total_videos || 0)}
          </div>
          <div className="text-xs text-gray-600 mt-1">
            小说: {stats?.total_novels || 0} | 视频: {stats?.total_videos || 0}
          </div>
        </div>
      </div>

      {/* 图表区域 */}
      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="col-span-2 bg-white rounded-xl p-6 border border-gray-200">
          <h2 className="text-lg font-semibold mb-4">收入趋势 (近30天)</h2>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={incomeTrend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Line type="monotone" dataKey="income" stroke="#22c55e" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <h2 className="text-lg font-semibold mb-4">最近注册用户</h2>
          <div className="space-y-3">
            {recentUsers.map((user) => (
              <div key={user.id} className="flex justify-between items-center text-sm">
                <span className="font-medium">{user.username}</span>
                <span className={`px-2 py-0.5 rounded-full text-xs ${
                  user.subscription_tier === 'professional' ? 'bg-yellow-100 text-yellow-700' :
                  user.subscription_tier === 'advanced' ? 'bg-blue-100 text-blue-700' :
                  'bg-green-100 text-green-700'
                }`}>
                  {user.subscription_tier === 'professional' ? '专业' :
                   user.subscription_tier === 'advanced' ? '进阶' : '基础'}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
