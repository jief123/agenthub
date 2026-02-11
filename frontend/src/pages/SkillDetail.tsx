import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getSkillById } from '../api/client'
import MarkdownRenderer from '../components/MarkdownRenderer'

interface Skill {
  id: number; name: string; description: string; version: string | null
  tags: string[]; git_url: string; installs: number; readme_html: string
  readme_content?: string; source: string
  author: { username: string }
}

export default function SkillDetail() {
  const { id } = useParams()
  const [skill, setSkill] = useState<Skill | null>(null)

  useEffect(() => {
    if (id) getSkillById(Number(id)).then((d) => setSkill(d as Skill)).catch(() => {})
  }, [id])

  if (!skill) return <div className="text-center py-12 text-gray-400">Loading...</div>

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">{skill.name}</h1>
        <p className="text-gray-500 mb-3">{skill.description}</p>
        <div className="flex items-center gap-3 text-sm text-gray-400 mb-3">
          <span>by <span className="text-gray-600">{skill.author.username}</span></span>
          {skill.version && <span>v{skill.version}</span>}
          <span>{skill.installs} installs</span>
          {skill.source === 'external' && (
            <span className="bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded text-xs">external</span>
          )}
        </div>
        {skill.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-4">
            {skill.tags.map((t) => (
              <span key={t} className="text-xs bg-gray-100 text-gray-600 px-2.5 py-1 rounded-full">{t}</span>
            ))}
          </div>
        )}
        <div className="bg-gray-900 text-gray-100 px-4 py-3 rounded-lg font-mono text-sm mb-6">
          uvx agenthub add {skill.name}
        </div>
        {skill.git_url && (
          <div className="text-sm text-gray-400 mb-6">
            <span className="text-gray-500">Repo:</span>{' '}
            <a href={skill.git_url} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline break-all">{skill.git_url}</a>
          </div>
        )}
      </div>

      {skill.readme_content ? (
        <MarkdownRenderer content={skill.readme_content} />
      ) : (
        <div className="prose prose-slate max-w-none" dangerouslySetInnerHTML={{ __html: skill.readme_html }} />
      )}
    </div>
  )
}
