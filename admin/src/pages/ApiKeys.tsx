import { useEffect, useState } from 'react'
import { apiKeysApi } from '../api'

export default function ApiKeys() {
  const [apiKeys, setApiKeys] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(false)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const pageSize = 20

  useEffect(() => {
    loadApiKeys()
  }, [page])

  const loadApiKeys = async () => {
    setLoading(true)
    try {
      const data = await apiKeysApi.list({
        skip: (page - 1) * pageSize,
        limit: pageSize,
      }) as any
      setApiKeys(data.items)
      setTotal(data.total)
    } catch (error) {
      console.error('加载API Key失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleRevoke = async (keyId: number) => {
    if (!confirm('确定要吊销该API Key吗？此操作不可恢复！')) return

    try {
      await apiKeysApi.revoke(keyId)
      loadApiKeys()
    } catch (error) {
      alert('吊销失败')
    }
  }

  const totalPages = Math.ceil(total / pageSize)

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">API Key 管理</h1>

      <div className="bg-white rounded-xl border border-gray-200">
        <div className="p-4 border-b border-gray-200 flex justify-between items-center">
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="搜索 Key / 用户..."
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm w-64"
            />
            <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200">
              搜索
            </button>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700"
          >
            + 创建 Key
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">Key ID</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">用户</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">名称</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">权限</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">调用次数</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">限流</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">状态</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">操作</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-gray-500">
                    加载中...
                  </td>
                </tr>
              ) : apiKeys.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-gray-500">
                    暂无数据
                  </td>
                </tr>
              ) : (
                apiKeys.map((key) => (
                  <tr key={key.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="px-4 py-3">ak_{key.id}</td>
                    <td className="px-4 py-3 font-medium">{key.user}</td>
                    <td className="px-4 py-3">{key.name}</td>
                    <td className="px-4 py-3 text-gray-600">
                      {key.permissions?.join(', ') || '全部'}
                    </td>
                    <td className="px-4 py-3">{key.usage_count?.toLocaleString() || 0}</td>
                    <td className="px-4 py-3">{key.rate_limit}/min</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                        key.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                      }`}>
                        {key.is_active ? '活跃' : '已吊销'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {key.is_active && (
                        <button
                          onClick={() => handleRevoke(key.id)}
                          className="px-3 py-1 bg-red-50 text-red-600 rounded text-xs font-medium hover:bg-red-100"
                        >
                          吊销
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
