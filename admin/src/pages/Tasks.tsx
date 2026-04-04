import { useEffect, useState } from 'react'
import { tasksApi } from '../api'

export default function Tasks() {
  const [stats, setStats] = useState<any>(null)
  const [tasks, setTasks] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadData()
    const interval = setInterval(loadData, 5000) // 每5秒刷新
    return () => clearInterval(interval)
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [statsData, tasksData] = await Promise.all([
        tasksApi.getStats(),
        tasksApi.list({ limit: 50 }),
      ]) as [any, any]
      setStats(statsData)
      setTasks(tasksData.items)
    } catch (error) {
      console.error('加载任务失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleStopTask = async (taskId: number) => {
    if (!confirm('确定要停止该任务吗？')) return

    try {
      await tasksApi.stop(taskId)
      loadData()
    } catch (error) {
      alert('停止任务失败')
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">任务监控</h1>

      {/* 统计卡片 */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-xl p-5 border border-gray-200">
          <div className="text-xs text-gray-500 mb-1">运行中</div>
          <div className="text-3xl font-bold text-green-600">{stats?.running || 0}</div>
        </div>
        <div className="bg-white rounded-xl p-5 border border-gray-200">
          <div className="text-xs text-gray-500 mb-1">排队中</div>
          <div className="text-3xl font-bold text-yellow-600">{stats?.queued || 0}</div>
        </div>
        <div className="bg-white rounded-xl p-5 border border-gray-200">
          <div className="text-xs text-gray-500 mb-1">今日完成</div>
          <div className="text-3xl font-bold text-indigo-600">{stats?.completed_today || 0}</div>
        </div>
        <div className="bg-white rounded-xl p-5 border border-gray-200">
          <div className="text-xs text-gray-500 mb-1">今日失败</div>
          <div className="text-3xl font-bold text-red-600">{stats?.failed_today || 0}</div>
        </div>
      </div>

      {/* 任务列表 */}
      <div className="bg-white rounded-xl border border-gray-200">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold">实时任务列表</h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">任务ID</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">用户</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">类型</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">状态</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">进度</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">当前Agent</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">耗时</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">操作</th>
              </tr>
            </thead>
            <tbody>
              {loading && tasks.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-gray-500">
                    加载中...
                  </td>
                </tr>
              ) : tasks.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-gray-500">
                    暂无任务
                  </td>
                </tr>
              ) : (
                tasks.map((task) => (
                  <tr key={task.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="px-4 py-3">T-{task.id}</td>
                    <td className="px-4 py-3 font-medium">{task.user}</td>
                    <td className="px-4 py-3">{task.task_type}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                        task.status === 'running' ? 'bg-green-100 text-green-700' :
                        task.status === 'queued' ? 'bg-yellow-100 text-yellow-700' :
                        task.status === 'completed' ? 'bg-blue-100 text-blue-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        {task.status === 'running' ? '运行中' :
                         task.status === 'queued' ? '排队中' :
                         task.status === 'completed' ? '已完成' : '失败'}
                      </span>
                    </td>
                    <td className="px-4 py-3">{task.progress || 0}%</td>
                    <td className="px-4 py-3 text-gray-600">{task.current_agent || '-'}</td>
                    <td className="px-4 py-3">{task.elapsed_time || 0}min</td>
                    <td className="px-4 py-3">
                      {(task.status === 'running' || task.status === 'queued') && (
                        <button
                          onClick={() => handleStopTask(task.id)}
                          className="px-3 py-1 bg-red-50 text-red-600 rounded text-xs font-medium hover:bg-red-100"
                        >
                          停止
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
