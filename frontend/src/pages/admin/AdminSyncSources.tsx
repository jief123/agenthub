import { useEffect, useState } from 'react'
import { getSyncSources, addSyncSource, deleteSyncSource, triggerSync, adminImport } from '../../api/client'

interface SyncSource { id: number; git_url: string; last_synced_at?: string }

export default function AdminSyncSources() {
  const [sources, setSources] = useState<SyncSource[]>([])
  const [url, setUrl] = useState('')
  const [importUrl, setImportUrl] = useState('')
  const [syncing, setSyncing] = useState<number | null>(null)
  const [msg, setMsg] = useState('')

  const load = () => { getSyncSources().then((d) => setSources(d as SyncSource[])).catch(() => {}) }
  useEffect(load, [])

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!url.trim()) return
    await addSyncSource(url)
    setUrl('')
    load()
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this sync source?')) return
    await deleteSyncSource(id)
    load()
  }

  const handleSync = async (id: number) => {
    setSyncing(id)
    try { await triggerSync(id); load() }
    finally { setSyncing(null) }
  }

  const handleImport = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!importUrl.trim()) return
    setMsg('Importing...')
    try {
      const result = await adminImport(importUrl) as unknown[]
      setMsg(`Imported ${result.length} skill(s)`)
      setImportUrl('')
    } catch (err) {
      setMsg(err instanceof Error ? err.message : 'Import failed')
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Sync Sources</h1>

      <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Quick Import from Git URL</h2>
        <form onSubmit={handleImport} className="flex gap-2">
          <input type="text" placeholder="https://github.com/..." value={importUrl}
            onChange={(e) => setImportUrl(e.target.value)}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
          <button type="submit" className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700">Import</button>
        </form>
        {msg && <p className="text-sm text-gray-500 mt-2">{msg}</p>}
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Add Sync Source</h2>
        <form onSubmit={handleAdd} className="flex gap-2">
          <input type="text" placeholder="Git repository URL" value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
          <button type="submit" className="px-4 py-2 bg-gray-900 text-white text-sm rounded-lg hover:bg-gray-800">Add</button>
        </form>
      </div>

      <div className="space-y-2">
        {sources.map((s) => (
          <div key={s.id} className="flex items-center justify-between bg-white rounded-lg border border-gray-200 px-4 py-3">
            <div>
              <div className="text-sm font-medium text-gray-900">{s.git_url}</div>
              {s.last_synced_at && <div className="text-xs text-gray-400">Last synced: {s.last_synced_at}</div>}
            </div>
            <div className="flex gap-2">
              <button onClick={() => handleSync(s.id)} disabled={syncing === s.id}
                className="text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50">
                {syncing === s.id ? 'Syncing...' : 'Sync'}
              </button>
              <button onClick={() => handleDelete(s.id)} className="text-sm text-red-500 hover:text-red-700">Delete</button>
            </div>
          </div>
        ))}
        {sources.length === 0 && <p className="text-sm text-gray-400 py-4 text-center">No sync sources configured.</p>}
      </div>
    </div>
  )
}
