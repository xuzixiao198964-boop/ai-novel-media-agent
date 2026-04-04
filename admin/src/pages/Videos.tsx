import { useEffect, useState } from 'react'
import { videosApi } from '../api'

export default function Videos() {
  const [videos, setVideos] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(false)
  const pageSize = 20

  useEffect(() => {
    loadVideos()
  }, [page])

  const loadVideos = async () => {
    setLoading(true)
    try {
      const data = await videosApi.list({
        skip: (page - 1) * pageSize,
        limit: pageSize,
      }) as any
      setVideos(data.items)
      setTotal(data.total)
    } catch (error) {
      console.error('加载视频失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatDuration = (seconds: number) => {
    if (!seconds) return '-'
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const totalPages = Math.ceil(total / pageSize)

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">视频作品管理</h1>

      <div className="bg-white rounded-xl border border-gray-200">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">ID</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">标题</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">作者</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">类型</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">时长</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">集数</th>
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
              ) : videos.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-gray-500">
                    暂无数据
                  </td>
                </tr>
              ) : (
                videos.map((video) => (
                  <tr key={video.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="px-4 py-3">V-{video.id}</td>
                    <td className="px-4 py-3 font-medium">{video.title}</td>
                    <td className="px-4 py-3 text-gray-600">{video.author}</td>
                    <td className="px-4 py-3">{video.video_type || '小说类'}</td>
                    <td className="px-4 py-3">{formatDuration(video.duration)}</td>
                    <td className="px-4 py-3">{video.episode_count || 1}集</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                        video.is_public ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'
                      }`}>
                        {video.is_public ? '已发布' : '草稿'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <button className="px-3 py-1 bg-gray-50 text-gray-600 rounded text-xs font-medium hover:bg-gray-100">
                        查看
                      </button>
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
