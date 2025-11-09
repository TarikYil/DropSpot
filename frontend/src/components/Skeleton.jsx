export function SkeletonCard() {
  return (
    <div className="card animate-pulse">
      <div className="h-48 w-full bg-gray-200 rounded-lg mb-4"></div>
      <div className="h-6 bg-gray-200 rounded w-3/4 mb-2"></div>
      <div className="h-4 bg-gray-200 rounded w-full mb-1"></div>
      <div className="h-4 bg-gray-200 rounded w-5/6 mb-4"></div>
      <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
      <div className="h-10 bg-gray-200 rounded"></div>
    </div>
  );
}

export function SkeletonText({ lines = 1, className = '' }) {
  return (
    <div className={className}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className={`h-4 bg-gray-200 rounded animate-pulse mb-2 ${
            i === lines - 1 ? 'w-3/4' : 'w-full'
          }`}
        ></div>
      ))}
    </div>
  );
}

export function SkeletonTable({ rows = 5, cols = 4 }) {
  return (
    <div className="card">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex space-x-4 pb-4 border-b">
          {Array.from({ length: cols }).map((_, i) => (
            <div key={i} className="flex-1 h-4 bg-gray-200 rounded animate-pulse"></div>
          ))}
        </div>
        {/* Rows */}
        {Array.from({ length: rows }).map((_, rowIdx) => (
          <div key={rowIdx} className="flex space-x-4">
            {Array.from({ length: cols }).map((_, colIdx) => (
              <div key={colIdx} className="flex-1 h-4 bg-gray-200 rounded animate-pulse"></div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

