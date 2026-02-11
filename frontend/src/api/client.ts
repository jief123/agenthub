const BASE = '/api/v1'

async function request(path: string, options: RequestInit = {}) {
  const apiKey = localStorage.getItem('token')
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  }
  if (apiKey) headers['Authorization'] = `Bearer ${apiKey}`

  const res = await fetch(`${BASE}${path}`, { ...options, headers })
  if (res.status === 401) {
    localStorage.removeItem('token')
    window.location.href = '/login'
    throw new Error('Unauthorized')
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(err.detail || 'Request failed')
  }
  if (res.status === 204) return null
  return res.json()
}

// Auth
export const registerUser = (username: string, email: string, password: string) =>
  request('/auth/register', { method: 'POST', body: JSON.stringify({ username, email, password }) })

export const loginUser = (email: string, password: string) =>
  request('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) })

export const getCurrentUser = () => request('/users/me')

// Skills
export const getTopSkills = (limit = 20) => request(`/skills/top?limit=${limit}`)
export const searchSkills = (q?: string, tag?: string, page = 1) =>
  request(`/skills?keyword=${q || ''}&tag=${tag || ''}&page=${page}`)
export const getSkillById = (id: number) => request(`/skills/${id}`)

// MCPs
export const getTopMcps = (limit = 20) => request(`/mcps/top?limit=${limit}`)
export const getMcpById = (id: number) => request(`/mcps/${id}`)

// Agents
export const getTopAgents = (limit = 20) => request(`/agents/top?limit=${limit}`)
export const getAgentById = (id: number) => request(`/agents/${id}`)

// Search
export const searchAll = (q?: string, type?: string, page = 1) => {
  const params = new URLSearchParams()
  if (q) params.set('q', q)
  if (type) params.set('type', type)
  params.set('page', String(page))
  return request(`/search?${params.toString()}`)
}

// Profile
export const getMyPublished = () => request('/users/me/published')
export const getMyInstalled = () => request('/users/me/installed')
export const getMyStats = () => request('/users/me/stats')
export const regenerateApiKey = () =>
  request('/users/me/api-key/regenerate', { method: 'POST' })

// Admin
export const getAdminAssets = (type?: string, page = 1) => {
  const params = new URLSearchParams()
  if (type) params.set('type', type)
  params.set('page', String(page))
  return request(`/admin/assets?${params.toString()}`)
}
export const deleteAdminAsset = (type: string, id: number) =>
  request(`/admin/assets/${type}/${id}`, { method: 'DELETE' })
export const getAdminUsers = (page = 1) => request(`/admin/users?page=${page}`)
export const getSyncSources = () => request('/admin/sync-sources')
export const addSyncSource = (git_url: string) =>
  request('/admin/sync-sources', { method: 'POST', body: JSON.stringify({ git_url }) })
export const deleteSyncSource = (id: number) =>
  request(`/admin/sync-sources/${id}`, { method: 'DELETE' })
export const triggerSync = (id: number) =>
  request(`/admin/sync-sources/${id}/sync`, { method: 'POST' })
export const adminImport = (git_url: string) =>
  request('/admin/import', { method: 'POST', body: JSON.stringify({ git_url }) })
