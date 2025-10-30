/**
 * Stats Card Component
 * Displays a single metric with label, value, and optional trend
 */

interface StatsCardProps {
  label: string;
  value: string | number;
  icon?: string;
  trend?: {
    value: number;
    direction: 'up' | 'down' | 'stable';
  };
  loading?: boolean;
}

export default function StatsCard({ label, value, icon, trend, loading }: StatsCardProps) {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-1/2 mb-3"></div>
        <div className="h-8 bg-gray-200 rounded w-3/4"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-1">{label}</p>
          <p className="text-3xl font-bold text-gray-900">{value}</p>

          {trend && (
            <div className="mt-2 flex items-center gap-1">
              {trend.direction === 'up' && (
                <span className="text-green-600 text-sm">↑ {trend.value}%</span>
              )}
              {trend.direction === 'down' && (
                <span className="text-red-600 text-sm">↓ {trend.value}%</span>
              )}
              {trend.direction === 'stable' && (
                <span className="text-gray-600 text-sm">→ {trend.value}%</span>
              )}
              <span className="text-xs text-gray-500">vs last period</span>
            </div>
          )}
        </div>

        {icon && (
          <div className="text-4xl opacity-50">{icon}</div>
        )}
      </div>
    </div>
  );
}
