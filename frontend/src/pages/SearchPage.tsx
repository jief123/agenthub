import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { searchAll } from '../api/client'
import AssetCard from '../components/AssetCard'

const TYPES = [
  { key: '', label: 'All' },
  { key: 'skill', label: 'Skills' },
  { key: 'mcp', label: 'MCP Servers' },
  { key: 'agent', label: 'Agents' },
]

interface Asset {
  id: number; name: string; description: string; version?: string | null
  tags?: string[]; installs: number; author: { username: string }; git_url?: string
}

export default function SearchPage() {
  const [params, setParams] = useSearchParams()
  const q = params.get('q') || ''
  const type = params.get('type') || ''
  const [query, setQuery] = useState(q)
  const [results, setResults] = useState<{ skills?: { items: Asset[] }; mcps?: { items: Asset[] }; agents?: { items: Asset[] } }>({})

  useEffect(() => {
    searchAll(q, type || undefined).then((d) => setResults(d as typeof results)).catch(() => {})
  }, [q, type])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setParams({ q: query, type })
  }

  const allItems: (Asset & { _type: 'skill' | 'mcp' | 'agent' })[] = [
    ...(results.skills?.items || []).map((i) => ({ ...i, _type: 'skill' as const })),
    ...(results.mcps?.items || []).map((i) => ({ ...i, _type: 'mcp' as const })),
    ...(results.agents?.items || []).map((i) => ({ ...i, _type: 'agent' as const })),
  ]

  return (
    <div>
      <form onSubmit={handleSearch} className="mb-6">
        <input
          type="text"
          placeholder="Search..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full max-w-lg px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
        />
      </form>

      <div className="flex gap-2 mb-6">
        {TYPES.map((t) => (
          <button
            key={t.key}
            onClick={() => setParams({ q, type: t.key })}
            className={`px-3 py-1.5 text-sm rounded-full ${
              type === t.key
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="grid gap-3">
        {allItems.map((item) => (
          <AssetCard
            key={`${item._type}-${item.id}`}
            id={item.id}
            name={item.name}
            description={item.description}
            type={item._type}
            tags={item.tags}
            installs={item.installs}
            author_username={item.author?.username || 'unknown'}
            version={item.version}
            git_url={item.git_url}
          />
        ))}
      </div>
      {allItems.length === 0 && q && (
        <p className="text-center text-gray-400 py-12">No results found for "{q}"</p>
      )}
    </div>
  )
}
