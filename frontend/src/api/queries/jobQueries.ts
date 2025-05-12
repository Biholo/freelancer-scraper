import { useQuery } from '@tanstack/react-query';
import { AnalyticsFilter, Freelancer, FreelancerAnalytics } from '@/types';
import { jobService } from '../jobService';

export const useFreelancers = (
  page = 1,
  limit = 10,
  filters?: Partial<AnalyticsFilter>
) => {
  return useQuery({
    queryKey: ['freelancers', page, limit, filters],
    queryFn: () => jobService.fetchFreelancers(page, limit, filters),
  });
};

export const useFreelancer = (id: string) => {
  return useQuery({
    queryKey: ['freelancer', id],
    queryFn: () => jobService.fetchFreelancerById(id),
    enabled: !!id,
  });
};

export const useAnalytics = (filters?: Partial<AnalyticsFilter>) => {
  return useQuery<FreelancerAnalytics>({
    queryKey: ['analytics', filters],
    queryFn: () => jobService.fetchAnalytics(filters),
  });
};

export const useCountries = () => {
  return useQuery({
    queryKey: ['countries'],
    queryFn: () => jobService.fetchCountries(),
  });
};

export const useRecentReviews = (limit = 10) => {
  return useQuery({
    queryKey: ['recentReviews', limit],
    queryFn: () => jobService.fetchRecentReviews(limit),
  });
};

export const useReviewKeywords = () => {
  return useQuery({
    queryKey: ['reviewKeywords'],
    queryFn: () => jobService.fetchReviewKeywords(),
  });
};

export const useSkills = () => {
  return useQuery({
    queryKey: ['skills'],
    queryFn: () => jobService.fetchSkills(),
  });
};

export const useSources = () => {
  return useQuery({
    queryKey: ['sources'],
    queryFn: () => jobService.fetchSources(),
  });
}; 