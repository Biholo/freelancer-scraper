import React from 'react';
import { useFreelancers } from '@/api/queries/jobQueries';
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

// Données de secours pour le développement
const fallbackPerformers = [
  {
    _id: "1",
    name: "Sarah Johnson",
    skills: ["Web Design", "UI/UX", "React"],
    rating: 4.9,
    reviews_count: 37,
    hourly_rate: 45,
    country: { name: "United States", flag: "🇺🇸" },
    source: "Freelancer"
  },
  {
    _id: "2",
    name: "Michael Chen",
    skills: ["Node.js", "MongoDB", "API Development"],
    rating: 4.8,
    reviews_count: 28,
    hourly_rate: 55,
    country: { name: "Canada", flag: "🇨🇦" },
    source: "PeoplePerHour"
  },
  {
    _id: "3",
    name: "Emma Davies",
    skills: ["Logo Design", "Branding", "Illustration"],
    rating: 4.7,
    reviews_count: 42,
    hourly_rate: 40,
    country: { name: "United Kingdom", flag: "🇬🇧" },
    source: "Truelancer"
  },
  {
    _id: "4",
    name: "Alejandro Gomez",
    skills: ["WordPress", "PHP", "Web Development"],
    rating: 4.9,
    reviews_count: 31,
    hourly_rate: 38,
    country: { name: "Spain", flag: "🇪🇸" },
    source: "Freelancer"
  },
  {
    _id: "5",
    name: "Priya Patel",
    skills: ["Mobile Development", "React Native", "Flutter"],
    rating: 4.8,
    reviews_count: 24,
    hourly_rate: 50,
    country: { name: "India", flag: "🇮🇳" },
    source: "PeoplePerHour"
  }
];

const TopPerformers: React.FC = () => {
  // Récupérer des freelancers avec un limit élevé puis filtre pour les meilleurs
  const { data, isLoading, error } = useFreelancers(1, 100);

  if (isLoading) return <Loader />;
  
  if (error || !data) {
    console.warn("Erreur ou pas de données, utilisation des données de secours");
    return renderPerformers(fallbackPerformers);
  }
  
  // Trier par évaluation (rating) et nombre d'avis
  const topPerformers = [...data.data]
    .filter(freelancer => freelancer.rating >= 4.5 && freelancer.reviews_count >= 5)
    .sort((a, b) => {
      // D'abord par note
      if (b.rating !== a.rating) {
        return b.rating - a.rating;
      }
      // Ensuite par nombre d'avis
      return b.reviews_count - a.reviews_count;
    })
    .slice(0, 5); // Prendre les 5 meilleurs
  
  if (topPerformers.length === 0) {
    return renderPerformers(fallbackPerformers);
  }
  
  return renderPerformers(topPerformers);
  
  function renderPerformers(performers: any[]) {
    return (
      <div className="overflow-y-auto max-h-[300px]">
        <ul className="space-y-3">
          {performers.map((freelancer: any) => (
            <li key={freelancer._id} className="flex items-center p-3 border rounded-lg hover:bg-gray-50">
              <div className="flex-grow">
                <div className="flex justify-between mb-1">
                  <h3 className="font-semibold">{freelancer.name}</h3>
                  <div className="flex items-center">
                    <span className="mr-1">{parseFloat(freelancer.rating).toFixed(1)}</span>
                    <StarRating rating={freelancer.rating} />
                  </div>
                </div>
                <div className="text-sm text-gray-600">
                  <div className="flex justify-between">
                    <span>{freelancer.skills.slice(0, 2).join(", ")}</span>
                    <span className="font-medium">${freelancer.hourly_rate}/hr</span>
                  </div>
                </div>
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>{freelancer.country?.flag || ""} {freelancer.country?.name || "Unknown"}</span>
                  <span>{freelancer.reviews_count} reviews</span>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    );
  }
};

export default TopPerformers; 