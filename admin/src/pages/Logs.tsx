import { useEffect, useState } from 'react'
import { logsApi } from '../api'

export default function Logs() {
  const [logs, setLogs] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [level, setLevel] = useState('')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(false)
  const pageSize = 50

  useEffect(() => {
    loadLogs()
  }, [page, level])

  const loadLogs = async () => {
    setLoading(true)
    try {
      const data = await logsApi.list({
        skip: (page - 1) * pageSize,
        limit: pageSize,
        level: level || undefined,
        search: search || undefined,
      }) as any
      setLogs(data.items)
      setTotal(data.total)
    } catch (error) {
      console.error('加载日志失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const totalPages = Math.ceil(total / pageSize)

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">系统日志</h1>

      <div className="bg-white rounded-xl border border-gray-200">
        <div className="p-4 border-b border-gray-200 flex gap-2">
          <select
            value={level}
            onChange={(e) => setLevel(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
          >
            <option value="">全部级别</option>
            <option value="ERROR">ERROR</option>
            <option value="WARN">WARN</option>
            <option value="INFO">INFO</option>
          </select>
          <input
            type="text"
            placeholder="搜索关键词..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm flex-1"
          />
          <button
            onClick={() => loadLogs()}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700"
          >
            搜索
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">时间</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">级别</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">模块</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">消息</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={4} className="px-4 py-8 text-center text-gray-500">
                    加载中...
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-4 py-8 text-center text-gray-500">
                    暂无日志
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="px-4 py-3 text-gray-600">
                      {log.created_at ? new Date(log.created_at).toLocaleTimeString() : '-'}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                        log.level === 'ERROR' ? 'bg-red-100 text-red-700' :
                        log.level === 'WARN' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-green-100 text-green-700'
                      }`}>
                        {log.level}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-medium">{log.module}</td>
                    <td className="px-4 py-3 text-gray-700">{log.message}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {totalPages > 1 && (
          <div className="p-4 border-t border-gray-200 flex justify-center gap-1">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
              className="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-50"
            >
              «
            </button>
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => (
              <button
                key={i + 1}
                onClick={() => setPage(i + 1)}
                className={`px-3 py-1 border rounded text-sm ${
                  page === i + 1
                    ? 'bg-indigo-600 text-white border-indigo-600'
                    : 'border-gray-300 hover:bg-gray-50'
                }`}
              >
                {i + 1}
              </button>
            ))}
            <button
              onClick={() => setPage(Math.min(totalPages, page + 1))}
              disabled={page === totalPages}
              className="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-50"
            >
              »
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
