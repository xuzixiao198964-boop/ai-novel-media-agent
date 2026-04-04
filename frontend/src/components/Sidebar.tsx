import { NavLink } from 'react-router-dom'
import './Sidebar.css'

export default function Sidebar() {
  return (
    <div className="sidebar">
      <div className="logo">AI 创作平台</div>

      <div className="menu-group">
        <div className="menu-group-title">工作台</div>
        <NavLink to="/dashboard" className="menu-item">
          📊 仪表盘
        </NavLink>
        <NavLink to="/create" className="menu-item">
          ➕ 创建任务
        </NavLink>
        <NavLink to="/tasks" className="menu-item">
          📋 我的任务
        </NavLink>
      </div>

      <div className="menu-group">
        <div className="menu-group-title">作品</div>
        <NavLink to="/novels" className="menu-item">
          📖 小说作品
        </NavLink>
        <NavLink to="/videos" className="menu-item">
          🎬 视频作品
        </NavLink>
        <NavLink to="/square" className="menu-item">
          🏪 作品广场
        </NavLink>
      </div>

      <div className="menu-group">
        <div className="menu-group-title">账户</div>
        <NavLink to="/package" className="menu-item">
          📦 套餐管理
        </NavLink>
        <NavLink to="/recharge" className="menu-item">
          💰 充值
        </NavLink>
        <NavLink to="/billing" className="menu-item">
          📄 消费记录
        </NavLink>
        <NavLink to="/platforms" className="menu-item">
          🔗 平台绑定
        </NavLink>
        <NavLink to="/settings" className="menu-item">
          ⚙️ 设置
        </NavLink>
      </div>
    </div>
  )
}
