import { useState } from 'react';
import { useAnalytics } from '@/api/queries/jobQueries';
import { AnalyticsFilter } from '@/types';
import FilterPanel from './components/FilterPanel';
import CountryDistribution from './components/CountryDistribution';
import SkillDistribution from './components/SkillDistribution';
import RateAnalysis from './components/RateAnalysis';
import SourceDistribution from './components/SourceDistribution';
import RatingDistribution from './components/RatingDistribution';
import RecentReviewsList from './components/RecentReviewsList';
import ReviewKeywords from './components/ReviewKeywords';
import TopPerformers from './components/TopPerformers';
import Loader from '@/components/ui/Loader';

const Dashboard = () => {
  const [filters, setFilters] = useState<Partial<AnalyticsFilter>>({});
  const { data: analytics, isLoading, error } = useAnalytics(filters);

  const handleFilterChange = (newFilters: Partial<AnalyticsFilter>) => {
    setFilters(newFilters);
  };

  if (isLoading) return <Loader />;
  
  if (error) return <div className="text-red-500">Error loading analytics data: {error.toString()}</div>;

  if (!analytics) return null;

  // Vérifier si les données pour les graphiques sont disponibles
  const hasRatingData = analytics.ratingDistribution && analytics.ratingDistribution.length > 0;

  return (
    <div className="max-w-7xl w-full mx-auto">
      <h1 className="text-3xl font-bold mb-6">Freelancer Analytics Dashboard</h1>
      
      <FilterPanel onFilterChange={handleFilterChange} currentFilters={filters} />
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6 mt-8">
        <div className="bg-white p-4 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Freelancer by Country</h2>
          <CountryDistribution data={analytics.countryDistribution || []} />
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Main Skills Distribution</h2>
          <SkillDistribution data={analytics.skillDistribution || []} />
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Hourly Rate Analysis</h2>
          <RateAnalysis data={analytics.rateDistribution || []} />
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Top Rated Freelancers</h2>
          <TopPerformers />
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Freelancer Source</h2>
          <SourceDistribution data={analytics.sourceDistribution || []} />
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Rating Distribution</h2>
          {hasRatingData ? (
            <RatingDistribution data={analytics.ratingDistribution} />
          ) : (
            <div className="text-center text-gray-500 py-8">No rating distribution data available</div>
          )}
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Recent Reviews</h2>
          <RecentReviewsList />
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Review Keywords</h2>
          <ReviewKeywords />
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 