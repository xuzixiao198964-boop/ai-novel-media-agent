import { useEffect, useState } from 'react'
import { publishApi } from '../api'

export default function Publish() {
  const [records, setRecords] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(false)
  const pageSize = 20

  useEffect(() => {
    loadRecords()
  }, [page])

  const loadRecords = async () => {
    setLoading(true)
    try {
      const data = await publishApi.list({
        skip: (page - 1) * pageSize,
        limit: pageSize,
      }) as any
      setRecords(data.items)
      setTotal(data.total)
    } catch (error) {
      console.error('加载发布记录失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleRetry = async (recordId: number) => {
    if (!confirm('确定要重试发布吗？')) return

    try {
      await publishApi.retry(recordId)
      loadRecords()
    } catch (error) {
      alert('重试失败')
    }
  }

  const totalPages = Math.ceil(total / pageSize)

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">发布管理</h1>

      <div className="bg-white rounded-xl border border-gray-200">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">ID</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">内容</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">平台</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">状态</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">时间</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">操作</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                    加载中...
                  </td>
                </tr>
              ) : records.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                    暂无数据
                  </td>
                </tr>
              ) : (
                records.map((record) => (
                  <tr key={record.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="px-4 py-3">P-{record.id}</td>
                    <td className="px-4 py-3 font-medium">{record.content_title}</td>
                    <td className="px-4 py-3">{record.platform}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                        record.status === 'success' ? 'bg-green-100 text-green-700' :
                        record.status === 'pending' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        {record.status === 'success' ? '成功' :
                         record.status === 'pending' ? '审核中' : '失败'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-600">
                      {record.created_at ? new Date(record.created_at).toLocaleString() : '-'}
                    </td>
                    <td className="px-4 py-3">
                      {record.status === 'failed' ? (
                        <button
                          onClick={() => handleRetry(record.id)}
                          className="px-3 py-1 bg-indigo-50 text-indigo-600 rounded text-xs font-medium hover:bg-indigo-100"
                        >
                          重试
                        </button>
                      ) : (
                        <button className="px-3 py-1 bg-gray-50 text-gray-600 rounded text-xs font-medium hover:bg-gray-100">
                          详情
                        </button>
                      )}
                    </td>
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
