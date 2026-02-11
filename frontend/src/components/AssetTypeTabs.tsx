const TABS = [
  { key: 'skills', label: 'Skills' },
  { key: 'mcps', label: 'MCP Servers' },
  { key: 'agents', label: 'Agents' },
] as const

type TabKey = typeof TABS[number]['key']

interface Props {
  active: string
  onChange: (tab: TabKey) => void
}

export default function AssetTypeTabs({ active, onChange }: Props) {
  return (
    <div className="flex gap-1 border-b border-gray-200 mb-6">
      {TABS.map((tab) => (
        <button
          key={tab.key}
          onClick={() => onChange(tab.key)}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            active === tab.key
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  )
}
