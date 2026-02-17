import React from 'react';
import { cn } from '../utils/helpers';

interface SkeletonProps {
  className?: string;
}

/** Simple pulse skeleton block */
export const Skeleton: React.FC<SkeletonProps> = ({ className }) => (
  <div
    className={cn(
      'animate-pulse rounded-md bg-gray-200 dark:bg-gray-700',
      className,
    )}
  />
);

/** Skeleton for a snippet list row */
export const SnippetRowSkeleton: React.FC = () => (
  <div className="flex flex-col gap-2 px-4 py-3 border-b border-gray-100 dark:border-gray-800">
    <Skeleton className="h-4 w-3/4" />
    <Skeleton className="h-3 w-full" />
    <div className="flex gap-2">
      <Skeleton className="h-3 w-16" />
      <Skeleton className="h-3 w-12" />
      <Skeleton className="h-3 w-20" />
    </div>
  </div>
);

/** Skeleton for the snippet list panel */
export const SnippetListSkeleton: React.FC<{ count?: number }> = ({ count = 6 }) => (
  <div>
    {Array.from({ length: count }).map((_, i) => (
      <SnippetRowSkeleton key={i} />
    ))}
  </div>
);

/** Skeleton for snippet detail view */
export const SnippetDetailSkeleton: React.FC = () => (
  <div className="p-6 space-y-4">
    <Skeleton className="h-6 w-2/3" />
    <div className="flex gap-2">
      <Skeleton className="h-5 w-16 rounded-full" />
      <Skeleton className="h-5 w-20 rounded-full" />
    </div>
    <Skeleton className="h-4 w-1/4" />
    <div className="space-y-2 mt-6">
      <Skeleton className="h-3 w-full" />
      <Skeleton className="h-3 w-full" />
      <Skeleton className="h-3 w-5/6" />
      <Skeleton className="h-3 w-full" />
      <Skeleton className="h-3 w-3/4" />
    </div>
  </div>
);

/** Skeleton for stat cards on dashboard */
export const StatCardSkeleton: React.FC = () => (
  <div className="rounded-xl border border-gray-200 dark:border-gray-700 p-5 space-y-3">
    <Skeleton className="h-4 w-1/2" />
    <Skeleton className="h-8 w-1/3" />
    <Skeleton className="h-3 w-2/3" />
  </div>
);

/** Skeleton for dashboard page */
export const DashboardSkeleton: React.FC = () => (
  <div className="p-6 space-y-6">
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {Array.from({ length: 4 }).map((_, i) => (
        <StatCardSkeleton key={i} />
      ))}
    </div>
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div className="rounded-xl border border-gray-200 dark:border-gray-700 p-5 space-y-3">
        <Skeleton className="h-4 w-1/3" />
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-3 w-full" />
        ))}
      </div>
      <div className="rounded-xl border border-gray-200 dark:border-gray-700 p-5 space-y-3">
        <Skeleton className="h-4 w-1/3" />
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-3 w-full" />
        ))}
      </div>
    </div>
  </div>
);
