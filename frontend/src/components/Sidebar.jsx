export default function Sidebar({ tags, collections, onSelectCollection, statusIndicator }) {
  const statusColor = {
    connected: "bg-green-500",
    error: "bg-red-500",
    disconnected: "bg-yellow-500",
  }[statusIndicator] || "bg-gray-500";

  return (
    <div className="w-64 bg-slate-900 border-r border-slate-800 p-4 overflow-y-auto">
      {/* Header */}\n      <div className="mb-6">
        <div className="flex items-center gap-2 mb-2">
          <div className={`w-2 h-2 rounded-full ${statusColor}`} />
          <span className="text-xs text-slate-400">Backend {statusIndicator}</span>
        </div>
      </div>

      {/* Collections */}
      <div className="mb-6">
        <h3 className="text-xs uppercase text-slate-400 font-semibold mb-2">Collections</h3>
        <div className="space-y-1">
          <button
            onClick={() => onSelectCollection(null)}
            className="w-full text-left px-3 py-2 rounded text-sm text-slate-300 hover:bg-slate-800 transition"
          >
            All snippets
          </button>
          {collections.map((col) => (
            <button
              key={col.id}
              onClick={() => onSelectCollection(col.id)}
              className="w-full text-left px-3 py-2 rounded text-sm text-slate-300 hover:bg-slate-800 transition"
            >
              <div>{col.name}</div>
              <div className="text-xs text-slate-500">{col.count} items</div>
            </button>
          ))}
        </div>
      </div>

      {/* Tags */}
      <div>
        <h3 className="text-xs uppercase text-slate-400 font-semibold mb-2">Tags</h3>
        <div className="flex flex-wrap gap-1">
          {tags.map((tag) => (
            <span
              key={tag.id}
              className="px-2 py-1 bg-slate-800 rounded text-xs text-slate-300"
            >
              {tag.name} <span className="text-slate-500">({tag.count})</span>
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
