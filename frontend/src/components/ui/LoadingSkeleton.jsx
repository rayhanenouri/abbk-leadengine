/**
 * Loading Skeleton Component
 * Professional shimmer loading states for better UX
 */

export const LeadCardSkeleton = () => {
  return (
    <div className="bg-white rounded-2xl border border-neutral-200 p-6 animate-pulse">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="h-6 bg-neutral-200 rounded-lg w-3/4 mb-2"></div>
          <div className="h-4 bg-neutral-200 rounded-lg w-1/2"></div>
        </div>
      </div>

      {/* Badges */}
      <div className="flex gap-2 mb-4">
        <div className="h-7 w-24 bg-neutral-200 rounded-full"></div>
        <div className="h-7 w-20 bg-neutral-200 rounded-full"></div>
      </div>

      {/* Score Section */}
      <div className="flex items-center gap-4 mb-4 pb-4 border-b border-neutral-100">
        <div className="w-20 h-20 bg-neutral-200 rounded-2xl"></div>
        <div className="flex-1">
          <div className="h-3 bg-neutral-200 rounded w-20 mb-2"></div>
          <div className="h-4 bg-neutral-200 rounded w-32"></div>
        </div>
      </div>

      {/* Reasoning */}
      <div className="space-y-2 mb-4">
        <div className="h-3 bg-neutral-200 rounded w-full"></div>
        <div className="h-3 bg-neutral-200 rounded w-5/6"></div>
      </div>

      {/* Actions */}
      <div className="flex gap-3">
        <div className="flex-1 h-11 bg-neutral-200 rounded-xl"></div>
        <div className="flex-1 h-11 bg-neutral-200 rounded-xl"></div>
      </div>
    </div>
  );
};

export const DashboardSkeletonGrid = ({ count = 6 }) => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
      {Array.from({ length: count }).map((_, i) => (
        <LeadCardSkeleton key={i} />
      ))}
    </div>
  );
};

export const StatCardSkeleton = () => {
  return (
    <div className="bg-gradient-to-br from-neutral-50 to-white p-5 rounded-2xl border border-neutral-200 animate-pulse">
      <div className="flex items-center gap-3">
        <div className="w-11 h-11 bg-neutral-200 rounded-xl"></div>
        <div className="flex-1">
          <div className="h-8 bg-neutral-200 rounded w-16 mb-2"></div>
          <div className="h-3 bg-neutral-200 rounded w-20"></div>
        </div>
      </div>
    </div>
  );
};
