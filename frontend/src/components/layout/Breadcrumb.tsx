import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

interface BreadcrumbProps {
  freelancerName?: string;
}

const Breadcrumb: React.FC<BreadcrumbProps> = ({ freelancerName }) => {
  const location = useLocation();
  const pathSegments = location.pathname.split('/').filter(Boolean);

  // Map path segments to readable names
  const getReadableName = (segment: string): string => {
    if (segment === 'dashboard') return 'Dashboard';
    if (segment === 'freelancers') return 'Freelancers';
    if (freelancerName && pathSegments.length > 1 && pathSegments[0] === 'freelancers') {
      return freelancerName;
    }
    return segment;
  };

  return (
    <nav className="flex px-4 py-3 bg-white rounded-lg shadow-sm mb-6">
      <ol className="flex items-center space-x-2">
        <li>
          <Link 
            to="/" 
            className="text-blue-600 hover:text-blue-800 flex items-center"
          >
            <Home size={16} />
            <span className="sr-only">Home</span>
          </Link>
        </li>
        
        {pathSegments.map((segment, index) => {
          // Build the path up to this point
          const path = `/${pathSegments.slice(0, index + 1).join('/')}`;
          const isLast = index === pathSegments.length - 1;
          
          return (
            <React.Fragment key={segment}>
              <li className="flex items-center">
                <ChevronRight size={14} className="text-gray-400" />
              </li>
              <li>
                {isLast ? (
                  <span className="text-gray-700 font-medium">
                    {getReadableName(segment)}
                  </span>
                ) : (
                  <Link 
                    to={path}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    {getReadableName(segment)}
                  </Link>
                )}
              </li>
            </React.Fragment>
          );
        })}
      </ol>
    </nav>
  );
};

export default Breadcrumb; 