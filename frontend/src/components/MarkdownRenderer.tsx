import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import 'highlight.js/styles/github-dark.css'

const FRONTMATTER_RE = /^---\s*\n([\s\S]*?)\n---\s*\n?([\s\S]*)$/

function parseFrontmatter(content: string): { meta: Record<string, string>; body: string } {
  const match = content.trim().match(FRONTMATTER_RE)
  if (!match) return { meta: {}, body: content }

  const yamlStr = match[1]
  const body = match[2].trim()
  const meta: Record<string, string> = {}

  for (const line of yamlStr.split('\n')) {
    const idx = line.indexOf(':')
    if (idx > 0) {
      const key = line.slice(0, idx).trim()
      let val = line.slice(idx + 1).trim()
      // Strip surrounding quotes
      if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
        val = val.slice(1, -1)
      }
      meta[key] = val
    }
  }
  return { meta, body }
}

export default function MarkdownRenderer({ content }: { content: string }) {
  const { meta, body } = parseFrontmatter(content)
  const metaEntries = Object.entries(meta)

  return (
    <div>
      {metaEntries.length > 0 && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Metadata</h3>
          <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 text-sm">
            {metaEntries.map(([key, val]) => (
              <div key={key} className="contents">
                <dt className="font-medium text-gray-600">{key}</dt>
                <dd className="text-gray-800 break-words">{val}</dd>
              </div>
            ))}
          </dl>
        </div>
      )}
      {body && (
        <div className="prose prose-slate max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeHighlight]}>
            {body}
          </ReactMarkdown>
        </div>
      )}
    </div>
  )
}
