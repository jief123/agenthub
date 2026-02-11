import { Link, useLocation } from 'react-router-dom'
import type { ReactNode } from 'react'

const NAV_ITEMS = [
  { path: '/admin', label: 'Dashboard', exact: true },
  { path: '/admin/sync', label: 'Sync Sources' },
  { path: '/admin/assets', label: 'Assets' },
  { path: '/admin/users', label: 'Users' },
]

export default function AdminLayout({ children }: { children: ReactNode }) {
  const { pathname } = useLocation()

  return (
    <div className="flex gap-8">
      <aside className="w-48 shrink-0">
        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Admin</h2>
        <nav className="flex flex-col gap-1">
          {NAV_ITEMS.map((item) => {
            const active = item.exact ? pathname === item.path : pathname.startsWith(item.path)
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`px-3 py-2 rounded-md text-sm ${
                  active ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                {item.label}
              </Link>
            )
          })}
        </nav>
      </aside>
      <div className="flex-1 min-w-0">{children}</div>
    </div>
  )
}
