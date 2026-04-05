import { NavLink } from 'react-router-dom'
import { useAuthStore } from '../store/auth'

const menuItems = [
  { path: '/dashboard', icon: '📊', label: '数据概览' },
  { path: '/users', icon: '👥', label: '用户管理' },
  { path: '/novels', icon: '📖', label: '小说管理' },
  { path: '/videos', icon: '🎬', label: '视频管理' },
  { path: '/tasks', icon: '📋', label: '任务监控' },
  { path: '/apikeys', icon: '🔑', label: 'API Key' },
  { path: '/finance', icon: '💰', label: '财务报表' },
  { path: '/publish', icon: '📤', label: '发布管理' },
  { path: '/logs', icon: '📝', label: '系统日志' },
  { path: '/config', icon: '⚙️', label: '系统配置' },
]

export default function Sidebar() {
  const { username, logout } = useAuthStore()

  const handleLogout = () => {
    if (confirm('确定要退出登录吗？')) {
      logout()
    }
  }

  return (
    <div className="w-[220px] bg-gray-900 text-gray-200 fixed top-0 bottom-0 overflow-y-auto">
      <div className="px-4 pb-4 pt-5 border-b border-gray-800 mb-3">
        <div className="text-lg font-bold text-red-400">🛡️ 管理后台</div>
      </div>
      <nav>
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-2.5 px-4 py-2.5 text-[0.85rem] transition-all ${
                isActive
                  ? 'bg-gray-800 text-red-400 border-l-[3px] border-red-400'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-gray-100'
              }`
            }
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-800">
        <div className="text-xs text-gray-500 mb-2">管理员: {username || 'admin'}</div>
        <button
          onClick={handleLogout}
          className="w-full text-xs text-red-400 hover:text-red-300 text-left"
        >
          退出登录
        </button>
      </div>
    </div>
  )
}
