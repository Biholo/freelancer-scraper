import React, { useState } from 'react';
import { useFreelancers } from '@/api/queries/jobQueries';
import { AnalyticsFilter, Freelancer } from '@/types';
import FilterPanel from './components/FilterPanel';
import Loader from '@/components/ui/Loader';
import { Link } from 'react-router-dom';

interface StarRatingProps {
  rating: number | null;
}

const StarRating: React.FC<StarRatingProps> = ({ rating }) => {
  const displayRating = rating || 0;
  const hasRating = rating !== null && rating !== undefined;
  
  return (
    <div className="flex items-center">
      {[1, 2, 3, 4, 5].map((star) => (
        <svg
          key={star}
          className={`w-4 h-4 ${
            hasRating && star <= displayRating ? 'text-yellow-400' : 'text-gray-300'
          }`}
          aria-hidden="true"
          xmlns="http://www.w3.org/2000/svg"
          fill="currentColor"
          viewBox="0 0 22 20"
        >
          <path d="M20.924 7.625a1.523 1.523 0 0 0-1.238-1.044l-5.051-.734-2.259-4.577a1.534 1.534 0 0 0-2.752 0L7.365 5.847l-5.051.734A1.535 1.535 0 0 0 1.463 9.2l3.656 3.563-.863 5.031a1.532 1.532 0 0 0 2.226 1.616L11 17.033l4.518 2.375a1.534 1.534 0 0 0 2.226-1.617l-.863-5.03L20.537 9.2a1.523 1.523 0 0 0 .387-1.575Z" />
        </svg>
      ))}
      <span className="ml-1 text-sm text-gray-700">
        {hasRating ? rating.toFixed(1) : 'N/A'}
      </span>
    </div>
  );
};

const FreelancerCard: React.FC<{ freelancer: Freelancer }> = ({ freelancer }) => {
  // Placeholder image if thumbnail is not available
  const placeholderImage = 'https://via.placeholder.com/80x80?text=No+Image';
  
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
      <div className="p-5">
        <div className="flex justify-between items-start">
          <div className="flex gap-4 items-start">
            <div className="flex-shrink-0">
              <img
                src={freelancer.thumbnail || placeholderImage}
                alt={freelancer.name}
                className="w-16 h-16 rounded-full object-cover border-2 border-gray-200"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = placeholderImage;
                }}
              />
            </div>
            <div>
              <h2 className="text-xl font-semibold mb-1">{freelancer.name}</h2>
              <p className="text-gray-500 text-sm">{freelancer.country?.name || 'Unknown location'}</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-lg font-bold text-green-600">${freelancer.hourly_rate || 'N/A'}/hr</p>
            {(freelancer.min_price || freelancer.max_price) ? (
              <p className="text-xs text-gray-500">
                Projects: ${freelancer.min_price || 0} 
                {freelancer.max_price ? ` - $${freelancer.max_price}` : ''}
              </p>
            ) : (
              <p className="text-xs text-gray-500">No project pricing information</p>
            )}
          </div>
        </div>
        
        <div className="mt-3">
          <p className="text-gray-700 font-medium">Main skill: {freelancer.main_skill || 'Not specified'}</p>
          
          <div className="flex flex-wrap gap-1 mt-2">
            {freelancer.skills?.slice(0, 5).map((skill, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
              >
                {skill}
              </span>
            ))}
            {freelancer.skills?.length > 5 && (
              <span className="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded-full">
                +{freelancer.skills.length - 5} more
              </span>
            )}
          </div>
        </div>
        
        <div className="mt-4 flex justify-between items-center">
          <StarRating rating={freelancer.rating} />
          <div className="text-sm text-gray-600">
            {freelancer.reviews_count || 0} review{(freelancer.reviews_count !== 1) ? 's' : ''}
          </div>
        </div>
        
        <div className="mt-4 pt-3 border-t">
          <Link
            to={`/freelancers/${freelancer._id}`}
            className="block w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white text-center rounded-md transition-colors"
          >
            View Profile
          </Link>
        </div>
      </div>
    </div>
  );
};

const FreelancerList: React.FC = () => {
  const [filters, setFilters] = useState<Partial<AnalyticsFilter>>({});
  const [page, setPage] = useState(1);
  const ITEMS_PER_PAGE = 9;
  
  const { data, isLoading, error } = useFreelancers(page, ITEMS_PER_PAGE, filters);
  
  const handleFilterChange = (newFilters: Partial<AnalyticsFilter>) => {
    setFilters(newFilters);
    setPage(1); // Reset to first page when filters change
  };
  
  const handlePreviousPage = () => {
    setPage(prev => Math.max(1, prev - 1));
  };
  
  const handleNextPage = () => {
    setPage(prev => {
      if (!data) return prev;
      const maxPage = Math.ceil(data.total / ITEMS_PER_PAGE);
      return Math.min(maxPage, prev + 1);
    });
  };
  
  return (
    <div className="max-w-7xl w-full mx-auto">
      <h1 className="text-3xl font-bold mb-6">Freelancers</h1>
      
      <FilterPanel onFilterChange={handleFilterChange} currentFilters={filters} />
      
      {isLoading ? (
        <div className="flex justify-center py-8">
          <Loader />
        </div>
      ) : error ? (
        <div className="text-center text-red-500 py-8">Error loading freelancers</div>
      ) : !data?.data?.length ? (
        <div className="text-center text-gray-500 py-8">No freelancers found matching your criteria</div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
            {data.data.map((freelancer) => (
              <FreelancerCard key={freelancer._id} freelancer={freelancer} />
            ))}
          </div>
          
          <div className="mt-8 flex justify-between items-center">
            <p className="text-gray-600">
              Showing {((page - 1) * ITEMS_PER_PAGE) + 1} - 
              {Math.min(page * ITEMS_PER_PAGE, data.total)} of {data.total} freelancers
            </p>
            
            <div className="flex space-x-2">
              <button
                onClick={handlePreviousPage}
                disabled={page === 1}
                className={`px-4 py-2 rounded-md ${
                  page === 1
                    ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Previous
              </button>
              
              <button
                onClick={handleNextPage}
                disabled={page * ITEMS_PER_PAGE >= data.total}
                className={`px-4 py-2 rounded-md ${
                  page * ITEMS_PER_PAGE >= data.total
                    ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default FreelancerList; 