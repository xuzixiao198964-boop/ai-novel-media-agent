import { useUserStore } from '../store/userStore'
import './Topbar.css'

export default function Topbar() {
  const user = useUserStore((state) => state.user)

  return (
    <div className="topbar">
      <div className="topbar-left"></div>
      <div className="topbar-right">
        <div className="balance">
          余额: <span>¥ {user?.balance.toFixed(2)}</span>
        </div>
        <div className="user-avatar">
          {user?.username.charAt(0).toUpperCase()}
        </div>
      </div>
    </div>
  )
}
