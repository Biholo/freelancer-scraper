import React, { useEffect } from 'react';
import { useRecentReviews } from '@/api/queries/jobQueries';
import Loader from '@/components/ui/Loader';

interface StarRatingProps {
  rating: number;
}

const StarRating: React.FC<StarRatingProps> = ({ rating }) => {
  return (
    <div className="flex">
      {[1, 2, 3, 4, 5].map((star) => (
        <svg
          key={star}
          className={`w-4 h-4 ${
            star <= rating ? 'text-yellow-400' : 'text-gray-300'
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
  );
};

// Données de review de secours pour le développement
const fallbackReviews = [
  {
    freelancer: {
      name: 'John Doe',
      _id: 'f1',
    },
    review: {
      _id: 'r1',
      freelancer_id: 'f1',
      rating: 5,
      title: 'Excellent work!',
      text: 'John delivered the project on time and with excellent quality. Would definitely hire again!',
      created_at: new Date().toISOString(),
    }
  },
  {
    freelancer: {
      name: 'Jane Smith',
      _id: 'f2',
    },
    review: {
      _id: 'r2',
      freelancer_id: 'f2',
      rating: 4,
      title: 'Great communication',
      text: 'Jane was very responsive and understood the requirements perfectly. The work was delivered as expected.',
      created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    }
  },
  {
    freelancer: {
      name: 'Alex Johnson',
      _id: 'f3',
    },
    review: {
      _id: 'r3',
      freelancer_id: 'f3',
      rating: 4.5,
      text: 'Alex is very skilled and delivered high-quality work. The only issue was a slight delay in delivery.',
      created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    }
  }
];

const RecentReviewsList: React.FC = () => {
  const { data: reviews, isLoading, error } = useRecentReviews(10);

  useEffect(() => {
    if (error) {
      console.error("Error loading reviews:", error);
    }
  }, [error]);

  if (isLoading) return <Loader />;
  
  // Utiliser les données de l'API si disponibles, sinon utiliser les données de secours
  const reviewsToDisplay = reviews && reviews.length > 0 ? reviews : fallbackReviews;

  return (
    <div className="overflow-y-auto max-h-[300px]">
      <ul className="space-y-4">
        {reviewsToDisplay.map((reviewData, index) => (
          <li key={index} className="p-3 border border-gray-200 rounded-lg">
            <div className="flex justify-between items-start mb-2">
              <div>
                <h3 className="font-semibold text-gray-800">
                  {reviewData.freelancer?.name || 'Unknown Freelancer'}
                </h3>
                <p className="text-xs text-gray-500">
                  {formatDate(reviewData.review?.created_at || '')}
                </p>
              </div>
              <StarRating rating={reviewData.review?.rating || 0} />
            </div>
            
            {reviewData.review?.title && (
              <h4 className="text-sm font-semibold mb-1">{reviewData.review.title}</h4>
            )}
            
            <p className="text-sm text-gray-700">
              {reviewData.review?.text 
                ? (reviewData.review.text.length > 120
                    ? `${reviewData.review.text.substring(0, 120)}...`
                    : reviewData.review.text)
                : 'No review text available'
              }
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
};

function formatDate(dateString: string) {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch (e) {
    return 'Invalid date';
  }
}

export default RecentReviewsList; 