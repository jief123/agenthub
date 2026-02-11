import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getTopSkills, getTopMcps, getTopAgents } from '../api/client'
import AssetTypeTabs from '../components/AssetTypeTabs'
import AssetCard from '../components/AssetCard'

type TabKey = 'skills' | 'mcps' | 'agents'

interface Asset {
  id: number; name: string; description: string; version?: string | null
  tags?: string[]; installs: number; author: { username: string }; git_url?: string
}

const FETCHERS: Record<TabKey, (n: number) => Promise<unknown>> = {
  skills: getTopSkills, mcps: getTopMcps, agents: getTopAgents,
}
const TYPE_MAP: Record<TabKey, 'skill' | 'mcp' | 'agent'> = {
  skills: 'skill', mcps: 'mcp', agents: 'agent',
}

export default function Home() {
  const [tab, setTab] = useState<TabKey>('skills')
  const [items, setItems] = useState<Asset[]>([])
  const [query, setQuery] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    FETCHERS[tab](20).then((d) => setItems(d as Asset[])).catch(() => setItems([]))
  }, [tab])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) navigate(`/search?q=${encodeURIComponent(query)}`)
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">AgentHub</h1>
        <p className="text-gray-500 mb-4">Discover and share AI agent skills, MCP servers, and configurations</p>
        <form onSubmit={handleSearch} className="max-w-lg">
          <input
            type="text"
            placeholder="Search skills, MCP servers, agents..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
          />
        </form>
      </div>

      <h2 className="text-xl font-semibold text-gray-900 mb-4">Leaderboard</h2>
      <AssetTypeTabs active={tab} onChange={setTab} />

      <div className="grid gap-3">
        {items.map((item) => (
          <AssetCard
            key={item.id}
            id={item.id}
            name={item.name}
            description={item.description}
            type={TYPE_MAP[tab]}
            tags={item.tags}
            installs={item.installs}
            author_username={item.author?.username || 'unknown'}
            version={item.version}
            git_url={item.git_url}
          />
        ))}
      </div>
      {items.length === 0 && (
        <p className="text-center text-gray-400 py-12">No assets registered yet.</p>
      )}
    </div>
  )
}
