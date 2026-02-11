import { Link } from 'react-router-dom'

interface Props {
  id: number
  name: string
  description: string
  type: 'skill' | 'mcp' | 'agent'
  tags?: string[]
  installs: number
  author_username: string
  version?: string | null
  git_url?: string | null
}

const TYPE_COLORS = {
  skill: 'bg-emerald-100 text-emerald-700',
  mcp: 'bg-purple-100 text-purple-700',
  agent: 'bg-amber-100 text-amber-700',
}

const TYPE_ROUTES = {
  skill: '/skills',
  mcp: '/mcps',
  agent: '/agents',
}

export default function AssetCard({ id, name, description, type, tags, installs, author_username, version, git_url }: Props) {
  return (
    <Link
      to={`${TYPE_ROUTES[type]}/${id}`}
      className="block p-4 rounded-lg border border-gray-200 hover:border-blue-300 hover:shadow-sm transition-all"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-semibold text-gray-900 truncate">{name}</h3>
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${TYPE_COLORS[type]}`}>
              {type}
            </span>
            {version && <span className="text-xs text-gray-400">v{version}</span>}
          </div>
          <p className="text-sm text-gray-500 line-clamp-2">{description}</p>
          {tags && tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {tags.slice(0, 5).map((t) => (
                <span key={t} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                  {t}
                </span>
              ))}
            </div>
          )}
        </div>
        <div className="text-right shrink-0">
          <div className="text-sm font-medium text-gray-700">{installs}</div>
          <div className="text-xs text-gray-400">installs</div>
        </div>
      </div>
      <div className="mt-2 text-xs text-gray-400">by {author_username}</div>
      {git_url && (
        <div className="mt-1 text-xs text-gray-400 truncate" title={git_url}>
          <span className="text-gray-300">repo:</span>{' '}
          <span className="text-blue-400 hover:text-blue-500">{git_url}</span>
        </div>
      )}
    </Link>
  )
}
