import { useState, useEffect } from 'react';
import { useCountries, useSkills, useSources } from '@/api/queries/jobQueries';
import { AnalyticsFilter } from '@/types';
import Loader from '@/components/ui/Loader';

interface FilterPanelProps {
  onFilterChange: (filters: Partial<AnalyticsFilter>) => void;
  currentFilters: Partial<AnalyticsFilter>;
}

const FilterPanel = ({ onFilterChange, currentFilters }: FilterPanelProps) => {
  const { data: countries, isLoading: isLoadingCountries } = useCountries();
  const { data: skills, isLoading: isLoadingSkills } = useSkills();
  const { data: sources, isLoading: isLoadingSources } = useSources();
  const [filters, setFilters] = useState<Partial<AnalyticsFilter>>(currentFilters);
  
  const isLoading = isLoadingCountries || isLoadingSkills || isLoadingSources;

  useEffect(() => {
    // Update local state when props change
    setFilters(currentFilters);
  }, [currentFilters]);

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>) => {
    const { name, value, type } = e.target;
    
    // Handle numeric inputs
    const processedValue = type === 'number' ? (value ? Number(value) : undefined) : value;
    
    setFilters(prev => ({
      ...prev,
      [name]: processedValue === '' ? undefined : processedValue,
    }));
  };

  const handleApplyFilters = () => {
    onFilterChange(filters);
  };

  const handleResetFilters = () => {
    const emptyFilters = {};
    setFilters(emptyFilters);
    onFilterChange(emptyFilters);
  };

  if (isLoading) return <Loader />;

  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <h2 className="text-xl font-semibold mb-4">Filters</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Country</label>
          <select
            name="country"
            value={filters.country || ''}
            onChange={handleChange}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          >
            <option value="">All Countries</option>
            {countries?.map(country => (
              <option key={country._id} value={country.code}>
                {country.name}
              </option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Skill</label>
          <select
            name="skill"
            value={filters.skill || ''}
            onChange={handleChange}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          >
            <option value="">All Skills</option>
            {skills?.map(skill => (
              <option key={skill} value={skill}>
                {skill}
              </option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Source</label>
          <select
            name="source"
            value={filters.source || ''}
            onChange={handleChange}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          >
            <option value="">All Sources</option>
            {sources?.map(source => (
              <option key={source} value={source}>
                {source}
              </option>
            ))}
          </select>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Min Hourly Rate ($)</label>
          <input
            type="number"
            name="minRate"
            value={filters.minRate || ''}
            onChange={handleChange}
            min={0}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Max Hourly Rate ($)</label>
          <input
            type="number"
            name="maxRate"
            value={filters.maxRate || ''}
            onChange={handleChange}
            min={0}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Min Rating</label>
          <select
            name="minRating"
            value={filters.minRating || ''}
            onChange={handleChange}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          >
            <option value="">Any Rating</option>
            <option value="1">1+ Stars</option>
            <option value="2">2+ Stars</option>
            <option value="3">3+ Stars</option>
            <option value="4">4+ Stars</option>
            <option value="4.5">4.5+ Stars</option>
          </select>
        </div>
      </div>
      
      <div className="flex justify-end space-x-2">
        <button
          onClick={handleResetFilters}
          className="px-4 py-2 text-sm text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
        >
          Reset
        </button>
        <button
          onClick={handleApplyFilters}
          className="px-4 py-2 text-sm text-white bg-blue-600 rounded-md hover:bg-blue-700"
        >
          Apply Filters
        </button>
      </div>
    </div>
  );
};

export default FilterPanel; 