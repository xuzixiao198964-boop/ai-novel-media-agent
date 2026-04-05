import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/auth'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Users from './pages/Users'
import Novels from './pages/Novels'
import Videos from './pages/Videos'
import Tasks from './pages/Tasks'
import ApiKeys from './pages/ApiKeys'
import Finance from './pages/Finance'
import Publish from './pages/Publish'
import Logs from './pages/Logs'
import Config from './pages/Config'

function App() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

  if (!isAuthenticated) {
    return <Login />
  }

  return (
    <BrowserRouter basename="/admin">
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="users" element={<Users />} />
          <Route path="novels" element={<Novels />} />
          <Route path="videos" element={<Videos />} />
          <Route path="tasks" element={<Tasks />} />
          <Route path="apikeys" element={<ApiKeys />} />
          <Route path="finance" element={<Finance />} />
          <Route path="publish" element={<Publish />} />
          <Route path="logs" element={<Logs />} />
          <Route path="config" element={<Config />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
