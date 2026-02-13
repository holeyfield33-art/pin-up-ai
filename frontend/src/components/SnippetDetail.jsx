function isSafeUrl(url) {
  try {
    const parsed = new URL(url);
    return ["http:", "https:"].includes(parsed.protocol);
  } catch {
    return false;
  }
}

export default function SnippetDetail({ snippet, onDelete }) {
  if (!snippet) return null;

  return (
    <div className="p-4">
      <div className="flex justify-between items-start mb-4">
        <h2 className="text-xl font-bold text-slate-100">{snippet.title}</h2>
        <button
          onClick={onDelete}
          className="text-red-400 hover:text-red-300 text-sm"
        >
          ✕
        </button>
      </div>

      {snippet.language && (
        <div className="mb-3">
          <span className="text-xs bg-slate-700 px-2 py-1 rounded">{snippet.language}</span>
        </div>
      )}

      <div className="bg-slate-800 rounded p-3 mb-4">
        <pre className="text-sm text-slate-300 overflow-x-auto whitespace-pre-wrap break-words">
          {snippet.body}
        </pre>
      </div>

      {snippet.source && (
        <div className="mb-4 text-sm">
          <span className="text-slate-400">Source: </span>
          {isSafeUrl(snippet.source) ? (
            <a href={snippet.source} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">
              {snippet.source}
            </a>
          ) : (
            <span className="text-slate-300">{snippet.source}</span>
          )}
        </div>
      )}

      {snippet.tags && snippet.tags.length > 0 && (
        <div className="mb-4">
          <div className="text-xs text-slate-400 mb-2">Tags:</div>
          <div className="flex flex-wrap gap-2">
            {snippet.tags.map((tag) => (
              <span key={tag} className="px-2 py-1 bg-slate-700 rounded text-xs text-slate-200">
                {tag}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="text-xs text-slate-500 mt-4">
        Created: {new Date(snippet.created_at).toLocaleString()}
      </div>
    </div>
  );
}
