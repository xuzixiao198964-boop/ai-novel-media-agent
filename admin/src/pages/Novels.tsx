import { useEffect, useState } from 'react'
import { novelsApi } from '../api'

export default function Novels() {
  const [novels, setNovels] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('')
  const [loading, setLoading] = useState(false)
  const pageSize = 20

  useEffect(() => {
    loadNovels()
  }, [page, category])

  const loadNovels = async () => {
    setLoading(true)
    try {
      const data = await novelsApi.list({
        skip: (page - 1) * pageSize,
        limit: pageSize,
        search: search || undefined,
        category: category || undefined,
      }) as any
      setNovels(data.items)
      setTotal(data.total)
    } catch (error) {
      console.error('加载小说失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleTogglePublic = async (novelId: number, currentStatus: boolean) => {
    if (!confirm(`确定要${currentStatus ? '下架' : '上架'}该小说吗？`)) return

    try {
      await novelsApi.updateStatus(novelId, !currentStatus)
      loadNovels()
    } catch (error) {
      alert('操作失败')
    }
  }

  const handleDelete = async (novelId: number) => {
    if (!confirm('确定要删除该小说吗？此操作不可恢复！')) return

    try {
      await novelsApi.delete(novelId)
      loadNovels()
    } catch (error) {
      alert('删除失败')
    }
  }

  const totalPages = Math.ceil(total / pageSize)

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">小说作品管理</h1>

      <div className="bg-white rounded-xl border border-gray-200">
        <div className="p-4 border-b border-gray-200 flex justify-between items-center">
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="搜索小说标题..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm w-64"
            />
            <button
              onClick={() => loadNovels()}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700"
            >
              搜索
            </button>
          </div>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
          >
            <option value="">全部分类</option>
            <option value="儿童">儿童</option>
            <option value="男频">男频</option>
            <option value="女频">女频</option>
          </select>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">ID</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">标题</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">作者</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">分类</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">字数</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">广场</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">评分</th>
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
              ) : novels.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-gray-500">
                    暂无数据
                  </td>
                </tr>
              ) : (
                novels.map((novel) => (
                  <tr key={novel.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="px-4 py-3">N-{novel.id}</td>
                    <td className="px-4 py-3 font-medium">{novel.title}</td>
                    <td className="px-4 py-3 text-gray-600">{novel.author}</td>
                    <td className="px-4 py-3">{novel.category} · {novel.genre}</td>
                    <td className="px-4 py-3">{(novel.word_count / 10000).toFixed(1)}万</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                        novel.is_public ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                      }`}>
                        {novel.is_public ? '已发布' : '未发布'}
                      </span>
                    </td>
                    <td className="px-4 py-3">{novel.rating?.toFixed(1) || '-'}</td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleTogglePublic(novel.id, novel.is_public)}
                          className="px-3 py-1 bg-red-50 text-red-600 rounded text-xs font-medium hover:bg-red-100"
                        >
                          {novel.is_public ? '下架' : '上架'}
                        </button>
                        {!novel.is_public && (
                          <button
                            onClick={() => handleDelete(novel.id)}
                            className="px-3 py-1 bg-gray-50 text-gray-600 rounded text-xs font-medium hover:bg-gray-100"
                          >
                            删除
                          </button>
                        )}
                      </div>
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
