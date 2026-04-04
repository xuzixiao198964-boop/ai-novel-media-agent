import { useAuthStore } from '../store/auth'

export default function Topbar() {
  const { username, logout } = useAuthStore()

  const handleLogout = () => {
    if (confirm('确定要退出登录吗？')) {
      logout()
    }
  }

  return (
    <div className="h-16 bg-white border-b border-gray-200 flex items-center justify-end px-6">
      <div className="flex items-center gap-3 text-sm text-gray-600">
        <span>管理员: {username || 'admin'}</span>
        <span className="text-gray-300">|</span>
        <button
          onClick={handleLogout}
          className="text-indigo-600 hover:text-indigo-700 font-medium"
        >
          退出
        </button>
      </div>
    </div>
  )
}
