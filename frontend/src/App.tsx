import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import { ProtectedRoute, AdminRoute } from './components/ProtectedRoute'
import AdminLayout from './components/AdminLayout'
import Home from './pages/Home'
import SearchPage from './pages/SearchPage'
import SkillDetail from './pages/SkillDetail'
import Login from './pages/Login'
import Register from './pages/Register'
import Profile from './pages/Profile'
import AdminDashboard from './pages/admin/AdminDashboard'
import AdminSyncSources from './pages/admin/AdminSyncSources'
import AdminAssets from './pages/admin/AdminAssets'
import AdminUsers from './pages/admin/AdminUsers'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/skills/:id" element={<SkillDetail />} />
        <Route path="/mcps/:id" element={<SkillDetail />} />
        <Route path="/agents/:id" element={<SkillDetail />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
        <Route path="/admin" element={<AdminRoute><AdminLayout><AdminDashboard /></AdminLayout></AdminRoute>} />
        <Route path="/admin/sync" element={<AdminRoute><AdminLayout><AdminSyncSources /></AdminLayout></AdminRoute>} />
        <Route path="/admin/assets" element={<AdminRoute><AdminLayout><AdminAssets /></AdminLayout></AdminRoute>} />
        <Route path="/admin/users" element={<AdminRoute><AdminLayout><AdminUsers /></AdminLayout></AdminRoute>} />
      </Routes>
    </Layout>
  )
}
