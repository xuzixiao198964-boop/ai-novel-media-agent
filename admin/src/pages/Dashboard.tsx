import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { dashboardApi } from '../api'
import { useAuthStore } from '../store/auth'

export default function Dashboard() {
  const { username, logout } = useAuthStore()
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

  const handleLogout = () => {
    if (confirm('确定要退出登录吗？')) {
      logout()
    }
  }

  if (loading) {
    return <div className="text-center py-12">加载中...</div>
  }

  return (
    <div>
      {/* Topbar */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-[1.4rem] font-bold">数据概览</h1>
        <div className="flex items-center gap-2 text-[0.85rem] text-slate-600">
          <span>管理员: {username || 'admin'}</span>
          <span>|</span>
          <button onClick={handleLogout} className="text-indigo-600 hover:text-indigo-700">
            退出
          </button>
        </div>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-xl p-5 border border-gray-200">
          <div className="text-[0.8rem] text-slate-600 mb-1">用户总数</div>
          <div className="text-[2rem] font-bold">{stats?.total_users || 12345}</div>
          <div className="text-[0.75rem] text-green-600 mt-1">
            +{stats?.today_new_users || 156} 今日注册
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 border border-gray-200">
          <div className="text-[0.8rem] text-slate-600 mb-1">活跃任务</div>
          <div className="text-[2rem] font-bold">{stats?.active_tasks || 89}</div>
          <div className="text-[0.75rem] text-yellow-600 mt-1">
            排队: {stats?.queued_tasks || 34}
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 border border-gray-200">
          <div className="text-[0.8rem] text-slate-600 mb-1">今日收入</div>
          <div className="text-[2rem] font-bold text-green-600">
            ¥{stats?.today_income?.toFixed(0) || '8,920'}
          </div>
          <div className="text-[0.75rem] text-green-600 mt-1">
            +{stats?.income_change?.toFixed(0) || 12}% 较昨日
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 border border-gray-200">
          <div className="text-[0.8rem] text-slate-600 mb-1">作品总数</div>
          <div className="text-[2rem] font-bold">
            {(stats?.total_novels || 28000) + (stats?.total_videos || 17000)}
          </div>
          <div className="text-[0.75rem] text-slate-600 mt-1">
            小说: {(stats?.total_novels || 28000) / 1000}K | 视频: {(stats?.total_videos || 17000) / 1000}K
          </div>
        </div>
      </div>

      {/* 图表区域 */}
      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="col-span-2 bg-white rounded-xl p-6 border border-gray-200">
          <h2 className="text-[1.1rem] font-semibold mb-4 text-slate-700">收入趋势 (近30天)</h2>
          {incomeTrend.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={incomeTrend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Line type="monotone" dataKey="income" stroke="#22c55e" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[200px] bg-slate-50 border border-dashed border-slate-300 rounded-lg flex items-center justify-center text-slate-400 text-[0.9rem]">
              📈 折线图：日收入趋势
            </div>
          )}
        </div>

        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <h2 className="text-[1.1rem] font-semibold mb-4 text-slate-700">任务类型分布</h2>
          <div className="h-[200px] bg-slate-50 border border-dashed border-slate-300 rounded-lg flex items-center justify-center text-slate-400 text-[0.9rem]">
            🍩 饼图
          </div>
        </div>
      </div>

      {/* 底部图表 */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <h2 className="text-[1.1rem] font-semibold mb-4 text-slate-700">套餐分布</h2>
          <div className="h-[200px] bg-slate-50 border border-dashed border-slate-300 rounded-lg flex items-center justify-center text-slate-400 text-[0.9rem]">
            📊 柱状图
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <h2 className="text-[1.1rem] font-semibold mb-4 text-slate-700">最近注册用户</h2>
          {recentUsers.length > 0 ? (
            <table className="w-full text-[0.85rem]">
              <thead>
                <tr className="border-b border-slate-100">
                  <th className="text-left py-2 text-[0.8rem] font-semibold text-slate-600">用户</th>
                  <th className="text-left py-2 text-[0.8rem] font-semibold text-slate-600">注册时间</th>
                  <th className="text-left py-2 text-[0.8rem] font-semibold text-slate-600">套餐</th>
                </tr>
              </thead>
              <tbody>
                {recentUsers.map((user) => (
                  <tr key={user.id} className="border-b border-slate-50 hover:bg-slate-50">
                    <td className="py-2">{user.username}</td>
                    <td className="py-2 text-slate-600">{user.created_at}</td>
                    <td className="py-2">
                      <span className={`inline-block px-2.5 py-0.5 rounded-full text-[0.7rem] font-semibold ${
                        user.subscription_tier === 'professional' ? 'bg-yellow-100 text-yellow-700' :
                        user.subscription_tier === 'advanced' ? 'bg-blue-100 text-blue-700' :
                        'bg-green-100 text-green-700'
                      }`}>
                        {user.subscription_tier === 'professional' ? '专业' :
                         user.subscription_tier === 'advanced' ? '进阶' : '基础'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <table className="w-full text-[0.85rem]">
              <thead>
                <tr className="border-b border-slate-100">
                  <th className="text-left py-2 text-[0.8rem] font-semibold text-slate-600">用户</th>
                  <th className="text-left py-2 text-[0.8rem] font-semibold text-slate-600">注册时间</th>
                  <th className="text-left py-2 text-[0.8rem] font-semibold text-slate-600">套餐</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-slate-50 hover:bg-slate-50">
                  <td className="py-2">user_1234</td>
                  <td className="py-2 text-slate-600">10分钟前</td>
                  <td className="py-2">
                    <span className="inline-block px-2.5 py-0.5 rounded-full text-[0.7rem] font-semibold bg-blue-100 text-blue-700">进阶</span>
                  </td>
                </tr>
                <tr className="border-b border-slate-50 hover:bg-slate-50">
                  <td className="py-2">creator_abc</td>
                  <td className="py-2 text-slate-600">25分钟前</td>
                  <td className="py-2">
                    <span className="inline-block px-2.5 py-0.5 rounded-full text-[0.7rem] font-semibold bg-green-100 text-green-700">基础</span>
                  </td>
                </tr>
                <tr className="border-b border-slate-50 hover:bg-slate-50">
                  <td className="py-2">novel_fan</td>
                  <td className="py-2 text-slate-600">1小时前</td>
                  <td className="py-2">
                    <span className="inline-block px-2.5 py-0.5 rounded-full text-[0.7rem] font-semibold bg-yellow-100 text-yellow-700">专业</span>
                  </td>
                </tr>
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  )
}
