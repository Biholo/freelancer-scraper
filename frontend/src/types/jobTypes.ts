export interface Country {
  _id: string;
  name: string;
  code: string;
}

export interface Review {
  _id: string;
  title: string;
  text: string;
  rating: number;
  created_at: string;
  freelancer_id: string;
}

export interface Freelancer {
  _id: string;
  name: string;
  country_id: string;
  country?: Country;
  main_skill: string;
  hourly_rate: number;
  min_price: number;
  max_price: number;
  created_at: string;
  source: string;
  rating: number;
  reviews_count: number;
  reviews?: Review[];
  skills: string[];
  thumbnail?: string;
}

// Interface pour les statistiques globales
export interface StatsData {
  freelancersCount: number;
  countriesCount: number;
  servicesCount: number;
  reviewsCount: number;
  avgRating: number;
  topCountries: { name: string; code: string; count: number }[];
}

export interface FreelancerAnalytics {
  countryDistribution: { name: string; count: number }[];
  skillDistribution: { name: string; count: number }[];
  rateDistribution: { range: string; count: number }[];
  signupsByMonth: { month: string; count: number }[];
  sourceDistribution: { source: string; count: number }[];
  ratingDistribution: { rating: number; count: number }[];
  stats: StatsData;
}

export interface AnalyticsFilter {
  country?: string;
  skill?: string;
  minRate?: number;
  maxRate?: number;
  source?: string;
  minRating?: number;
  dateRange?: [Date, Date];
} 