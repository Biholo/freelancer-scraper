import React, { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useFreelancer, useFreelancers } from '@/api/queries/jobQueries';
import Loader from '@/components/ui/Loader';
import { ArrowLeft, ArrowRight, ChevronLeft, Home, List, ChevronRight } from 'lucide-react';
import Breadcrumb from '@/components/layout/Breadcrumb';

interface StarRatingProps {
  rating: number | null;
}

const StarRating: React.FC<StarRatingProps> = ({ rating }) => {
  const displayRating = rating || 0;
  const hasRating = rating !== null && rating !== undefined;
  
  return (
    <div className="flex">
      {[1, 2, 3, 4, 5].map((star) => (
        <svg
          key={star}
          className={`w-5 h-5 ${
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
      <span className="ml-2 text-gray-700">({hasRating ? rating.toFixed(1) : 'N/A'})</span>
    </div>
  );
};

const FreelancerDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: freelancer, isLoading, error } = useFreelancer(id || '');
  const { data: allFreelancers } = useFreelancers(1, 100);
  
  // État pour la pagination des commentaires
  const [reviewsPage, setReviewsPage] = useState(1);
  const REVIEWS_PER_PAGE = 5;

  // Find the current freelancer index and the next/previous freelancers
  let currentIndex = -1;
  let prevFreelancerId: string | null = null;
  let nextFreelancerId: string | null = null;
  
  if (allFreelancers?.data) {
    currentIndex = allFreelancers.data.findIndex(f => f._id === id);
    
    if (currentIndex > 0) {
      prevFreelancerId = allFreelancers.data[currentIndex - 1]._id;
    }
    
    if (currentIndex < allFreelancers.data.length - 1) {
      nextFreelancerId = allFreelancers.data[currentIndex + 1]._id;
    }
  }

  if (isLoading) return <Loader />;

  if (error) return <div className="text-center text-red-500 py-8">Error loading freelancer details</div>;

  if (!freelancer) return <div className="text-center text-gray-500 py-8">Freelancer not found</div>;

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };
  
  // Calculer les reviews à afficher pour la page courante
  const paginatedReviews = freelancer.reviews
    ? freelancer.reviews.slice(
        (reviewsPage - 1) * REVIEWS_PER_PAGE,
        reviewsPage * REVIEWS_PER_PAGE
      )
    : [];
  
  console.log('Reviews disponibles:', freelancer.reviews?.length || 0);
  console.log('Reviews affichées:', paginatedReviews.length);
  
  // Calculer le nombre total de pages
  const totalReviewsPages = freelancer.reviews
    ? Math.ceil(freelancer.reviews.length / REVIEWS_PER_PAGE)
    : 0;
  
  // Image par défaut si thumbnail n'est pas disponible
  const placeholderImage = 'https://via.placeholder.com/150x150?text=No+Image';

  return (
    <div className="max-w-7xl w-full mx-auto">
      <Breadcrumb freelancerName={freelancer.name} />
      
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center space-x-2">
          <Link 
            to="/freelancers" 
            className="flex items-center text-blue-600 hover:text-blue-800 transition-colors"
          >
            <ChevronLeft size={18} />
            <span>Back to Freelancers</span>
          </Link>
        </div>
        
        {/* Navigation buttons */}
        <div className="flex space-x-2">
          <Link 
            to="/dashboard" 
            className="inline-flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
          >
            <Home size={16} className="mr-2" />
            Dashboard
          </Link>
          
          <Link 
            to="/freelancers" 
            className="inline-flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
          >
            <List size={16} className="mr-2" />
            All Freelancers
          </Link>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="p-6">
          <div className="flex flex-col md:flex-row justify-between">
            <div className="flex flex-col md:flex-row gap-5">
              <div className="flex-shrink-0 mb-4 md:mb-0">
                <img
                  src={freelancer.thumbnail || placeholderImage}
                  alt={freelancer.name}
                  className="w-32 h-32 rounded-full object-cover border-4 border-gray-200"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = placeholderImage;
                  }}
                />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-800">{freelancer.name}</h1>
                <p className="text-gray-600 mt-1">
                  {freelancer.country?.name || 'Unknown location'} • Joined {formatDate(freelancer.created_at)}
                </p>
                <div className="mt-3">
                  <StarRating rating={freelancer.rating} />
                  <p className="text-gray-600 mt-1">
                    {freelancer.reviews_count} review{freelancer.reviews_count !== 1 ? 's' : ''}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="mt-4 md:mt-0 md:text-right">
              <div className="text-2xl font-bold text-green-600">${freelancer.hourly_rate || 'N/A'}/hr</div>
              {(freelancer.min_price || freelancer.max_price) ? (
                <p className="text-gray-600">
                  Projects from ${freelancer.min_price || 0}
                  {freelancer.max_price ? ` to $${freelancer.max_price}` : ''}
                </p>
              ) : (
                <p className="text-gray-600">No project pricing information</p>
              )}
              <p className="text-sm text-gray-500 mt-1">Source: {freelancer.source}</p>
            </div>
          </div>

          <div className="mt-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-3">Skills</h2>
            <div className="flex flex-wrap gap-2">
              {freelancer.main_skill && (
                <span className="px-3 py-1 bg-blue-500 text-white rounded-full">
                  {freelancer.main_skill} (Main)
                </span>
              )}
              {freelancer.skills?.map((skill, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full"
                >
                  {skill}
                </span>
              ))}
              {(!freelancer.skills || freelancer.skills.length === 0) && !freelancer.main_skill && (
                <span className="text-gray-500">No skills specified</span>
              )}
            </div>
          </div>

          {freelancer.reviews && Array.isArray(freelancer.reviews) && freelancer.reviews.length > 0 ? (
            <div className="mt-8" id="reviews-section">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-gray-800">Avis reçus par {freelancer.name}</h2>
                <div className="text-sm text-gray-600 bg-blue-50 px-3 py-1 rounded-full">
                  <span className="font-medium">{freelancer.reviews.length}</span> avis client
                </div>
              </div>
              
              <div className="bg-blue-50 p-3 rounded-lg mb-5">
                <p className="text-blue-800 text-sm">Ces avis ont été laissés par des clients qui ont travaillé avec {freelancer.name}. Ils reflètent la qualité du travail et la satisfaction des clients.</p>
              </div>
              
              <div className="space-y-6 mb-6">
                {paginatedReviews.length > 0 ? (
                  paginatedReviews.map((review, index) => (
                    <div key={index} className="border-b pb-5 last:border-b-0">
                      <div className="flex justify-between items-start">
                        <div>
                          {review.title ? (
                            <h3 className="font-semibold text-lg">{review.title}</h3>
                          ) : (
                            <h3 className="font-semibold text-lg text-gray-700">Avis client</h3>
                          )}
                          <p className="text-sm text-gray-500">
                            {formatDate(review.created_at)}
                          </p>
                        </div>
                        <div className="flex">
                          {[1, 2, 3, 4, 5].map((star) => (
                            <svg
                              key={star}
                              className={`w-4 h-4 ${
                                star <= (review.rating || 0) ? 'text-yellow-400' : 'text-gray-300'
                              }`}
                              aria-hidden="true"
                              xmlns="http://www.w3.org/2000/svg"
                              fill="currentColor"
                              viewBox="0 0 22 20"
                            >
                              <path d="M20.924 7.625a1.523 1.523 0 0 0-1.238-1.044l-5.051-.734-2.259-4.577a1.534 1.534 0 0 0-2.752 0L7.365 5.847l-5.051.734A1.535 1.535 0 0 0 1.463 9.2l3.656 3.563-.863 5.031a1.532 1.532 0 0 0 2.226 1.616L11 17.033l4.518 2.375a1.534 1.534 0 0 0 2.226-1.617l-.863-5.03L20.537 9.2a1.523 1.523 0 0 0 .387-1.575Z" />
                            </svg>
                          ))}
                        </div>
                      </div>
                      <div className="mt-2">
                        <div className="bg-gray-50 border-l-4 border-blue-500 p-3 rounded-r-md">
                          <p className="text-gray-700 italic">"{review.text}"</p>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-4 text-gray-500">
                    Aucun avis disponible pour cette page
                  </div>
                )}
              </div>
              
              {/* Pagination des reviews */}
              {totalReviewsPages > 1 && (
                <div className="flex justify-between items-center mt-6">
                  <button
                    onClick={() => setReviewsPage(prev => Math.max(1, prev - 1))}
                    disabled={reviewsPage === 1}
                    className={`flex items-center px-3 py-1 rounded ${
                      reviewsPage === 1
                        ? 'text-gray-400 cursor-not-allowed'
                        : 'text-blue-600 hover:text-blue-800'
                    }`}
                  >
                    <ChevronLeft size={16} className="mr-1" />
                    Previous
                  </button>
                  
                  <div className="flex space-x-1">
                    {Array.from({ length: totalReviewsPages }, (_, i) => i + 1).map(page => (
                      <button
                        key={page}
                        onClick={() => setReviewsPage(page)}
                        className={`w-8 h-8 rounded-full ${
                          page === reviewsPage
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {page}
                      </button>
                    ))}
                  </div>
                  
                  <button
                    onClick={() => setReviewsPage(prev => Math.min(totalReviewsPages, prev + 1))}
                    disabled={reviewsPage === totalReviewsPages}
                    className={`flex items-center px-3 py-1 rounded ${
                      reviewsPage === totalReviewsPages
                        ? 'text-gray-400 cursor-not-allowed'
                        : 'text-blue-600 hover:text-blue-800'
                    }`}
                  >
                    Next
                    <ChevronRight size={16} className="ml-1" />
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="mt-8 p-6 bg-gray-50 rounded-lg text-center">
              <h2 className="text-xl font-semibold text-gray-800 mb-3">Aucun avis client</h2>
              <p className="text-gray-600">Ce freelancer n'a pas encore reçu d'avis de clients.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FreelancerDetail; 