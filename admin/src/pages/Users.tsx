import { useEffect, useState } from 'react'
import { usersApi } from '../api'

export default function Users() {
  const [users, setUsers] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(false)
  const pageSize = 20

  useEffect(() => {
    loadUsers()
  }, [page, search])

  const loadUsers = async () => {
    setLoading(true)
    try {
      const data = await usersApi.list({
        skip: (page - 1) * pageSize,
        limit: pageSize,
        search: search || undefined,
      }) as any
      setUsers(data.items)
      setTotal(data.total)
    } catch (error) {
      console.error('加载用户失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleToggleStatus = async (userId: number, currentStatus: boolean) => {
    if (!confirm(`确定要${currentStatus ? '禁用' : '启用'}该用户吗？`)) return

    try {
      await usersApi.update(userId, { is_active: !currentStatus })
      loadUsers()
    } catch (error) {
      alert('操作失败')
    }
  }

  const totalPages = Math.ceil(total / pageSize)

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">用户管理</h1>

      <div className="bg-white rounded-xl border border-gray-200">
        {/* 工具栏 */}
        <div className="p-4 border-b border-gray-200 flex justify-between items-center">
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="搜索用户名/邮箱/手机..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm w-64"
            />
            <button
              onClick={() => loadUsers()}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700"
            >
              搜索
            </button>
          </div>
          <button className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50">
            导出
          </button>
        </div>

        {/* 表格 */}
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">ID</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">用户名</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">密码</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">套餐</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">余额</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">状态</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">注册时间</th>
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
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-gray-500">
                    暂无数据
                  </td>
                </tr>
              ) : (
                users.map((user) => (
                  <tr key={user.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="px-4 py-3">{user.id}</td>
                    <td className="px-4 py-3 font-medium">{user.username}</td>
                    <td className="px-4 py-3 text-gray-600 font-mono text-xs">{user.password || '******'}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                        user.subscription_tier === 'enterprise' ? 'bg-red-100 text-red-700' :
                        user.subscription_tier === 'professional' ? 'bg-yellow-100 text-yellow-700' :
                        user.subscription_tier === 'advanced' ? 'bg-blue-100 text-blue-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {user.subscription_tier === 'enterprise' ? '企业' :
                         user.subscription_tier === 'professional' ? '专业' :
                         user.subscription_tier === 'advanced' ? '进阶' : '基础'}
                      </span>
                    </td>
                    <td className="px-4 py-3">¥{user.balance?.toFixed(2) || '0.00'}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                        user.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                      }`}>
                        {user.is_active ? '正常' : '已禁用'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-600">
                      {user.created_at ? new Date(user.created_at).toLocaleDateString() : '-'}
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => handleToggleStatus(user.id, user.is_active)}
                        className={`px-3 py-1 rounded text-xs font-medium ${
                          user.is_active
                            ? 'bg-red-50 text-red-600 hover:bg-red-100'
                            : 'bg-green-50 text-green-600 hover:bg-green-100'
                        }`}
                      >
                        {user.is_active ? '禁用' : '启用'}
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* 分页 */}
        {totalPages > 1 && (
          <div className="p-4 border-t border-gray-200 flex justify-center gap-1">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
              className="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-50"
            >
              «
            </button>
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              const pageNum = i + 1
              return (
                <button
                  key={pageNum}
                  onClick={() => setPage(pageNum)}
                  className={`px-3 py-1 border rounded text-sm ${
                    page === pageNum
                      ? 'bg-indigo-600 text-white border-indigo-600'
                      : 'border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  {pageNum}
                </button>
              )
            })}
            {totalPages > 5 && <span className="px-2 py-1">...</span>}
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
