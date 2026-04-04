import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Layout from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import CreateTask from './pages/CreateTask'
import Tasks from './pages/Tasks'
import Novels from './pages/Novels'
import NovelDetail from './pages/NovelDetail'
import Videos from './pages/Videos'
import Package from './pages/Package'
import Recharge from './pages/Recharge'
import Billing from './pages/Billing'
import Platforms from './pages/Platforms'
import Settings from './pages/Settings'

// 受保护的路由组件
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuthStore()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

function App() {
  return (
    <Routes>
      {/* 公开路由 */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* 受保护的路由 */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="create" element={<CreateTask />} />
        <Route path="tasks" element={<Tasks />} />
        <Route path="novels" element={<Novels />} />
        <Route path="novel/:id" element={<NovelDetail />} />
        <Route path="videos" element={<Videos />} />
        <Route path="package" element={<Package />} />
        <Route path="recharge" element={<Recharge />} />
        <Route path="billing" element={<Billing />} />
        <Route path="platforms" element={<Platforms />} />
        <Route path="settings" element={<Settings />} />
      </Route>

      {/* 404 */}
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  )
}

export default App
