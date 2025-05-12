import { Freelancer, FreelancerAnalytics, AnalyticsFilter, Country, Review } from '@/types';
import { api } from '@/api/interceptor';

// Fallback à des données de mock uniquement si l'API ne répond pas
import freelancersData from '@/fixtures/freelancers.json';
import countriesData from '@/fixtures/countries.json';
import reviewsData from '@/fixtures/reviews.json';

class JobService {
  // Récupération des freelancers avec pagination et filtres
  public async fetchFreelancers(
    page = 1,
    limit = 10,
    filters?: Partial<AnalyticsFilter>
  ): Promise<{ data: Freelancer[]; total: number }> {
    try {
      let endpoint = `/api/freelancers?page=${page}&limit=${limit}`;
      
      // Ajout des filtres à l'URL
      if (filters) {
        if (filters.country) {
          endpoint += `&country=${filters.country}`;
        }
        
        if (filters.skill) {
          endpoint += `&skill=${filters.skill}`;
        }
        
        // Note: Le backend ne supporte pas directement minRate et maxRate,
        // ces filtres seront appliqués côté client après réception des données
      }
      
      const response = await api.fetchRequest(endpoint, "GET");
      
      // Récupérer tous les pays en une seule requête
      const countries = await this.fetchCountries();
      
      // Associer les pays aux freelancers
      const data = response.data.map((freelancer: Freelancer) => {
        if (freelancer.country_id) {
          const country = countries.find(c => c._id === freelancer.country_id);
          return { ...freelancer, country };
        }
        return freelancer;
      });
      
      return {
        data,
        total: response.meta.total
      };
    } catch (error) {
      console.error("Erreur lors de la récupération des freelancers:", error);
      // Fallback aux données de mock en cas d'erreur
      console.warn("Utilisation des données de mock pour les freelancers");
      
      // Simuler le filtrage et la pagination comme avant
      let filteredData = [...freelancersData];
      
      if (filters) {
        if (filters.country) {
          filteredData = filteredData.filter(f => f.country_id === filters.country);
        }
        if (filters.skill) {
          filteredData = filteredData.filter(f => 
            f.main_skill === filters.skill || 
            f.skills?.includes(filters.skill as string)
          );
        }
        if (filters.minRate !== undefined) {
          filteredData = filteredData.filter(f => f.hourly_rate >= (filters.minRate as number));
        }
        if (filters.maxRate !== undefined) {
          filteredData = filteredData.filter(f => f.hourly_rate <= (filters.maxRate as number));
        }
      }
      
      const total = filteredData.length;
      const startIndex = (page - 1) * limit;
      const endIndex = startIndex + limit;
      const paginatedData = filteredData.slice(startIndex, endIndex);
      
      const enrichedData = paginatedData.map(freelancer => {
        const country = countriesData.find(c => c._id === freelancer.country_id);
        return { ...freelancer, country };
      });
      
      return {
        data: enrichedData,
        total
      };
    }
  }

  // Récupération d'un freelancer par son ID
  public async fetchFreelancerById(id: string): Promise<Freelancer> {
    try {
      // Récupération du freelancer
      const freelancer = await api.fetchRequest(`/api/freelancers/${id}`, "GET");
      
      // Récupération du pays associé si nécessaire
      let country = null;
      if (freelancer.country_id) {
        // Récupérer tous les pays et trouver celui qui correspond
        const countries = await this.fetchCountries();
        country = countries.find(c => c._id === freelancer.country_id) || null;
      }
      
      // Récupération des reviews associées
      const reviews = await this.fetchFreelancerReviews(id);
      
      return {
        ...freelancer,
        country,
        reviews
      };
    } catch (error) {
      console.error(`Erreur lors de la récupération du freelancer ${id}:`, error);
      
      // Fallback aux données de mock
      console.warn("Utilisation des données de mock pour le freelancer");
      const freelancer = freelancersData.find(f => f._id === id);
      
      if (!freelancer) {
        throw new Error('Freelancer not found');
      }
      
      const country = countriesData.find(c => c._id === freelancer.country_id);
      const reviews = reviewsData.filter(r => r.freelancer_id === id);
      
      return {
        ...freelancer,
        country,
        reviews
      };
    }
  }

  // Récupération des pays
  public async fetchCountries(): Promise<Country[]> {
    try {
      return await api.fetchRequest('/api/countries', "GET");
    } catch (error) {
      console.error("Erreur lors de la récupération des pays:", error);
      // Fallback aux données de mock
      console.warn("Utilisation des données de mock pour les pays");
      return countriesData;
    }
  }


  // Récupération des reviews d'un freelancer
  private async fetchFreelancerReviews(freelancerId: string, page = 1, limit = 10): Promise<Review[]> {
    try {
      console.log(`Fetching reviews for freelancer: ${freelancerId}`);
      const response = await api.fetchRequest(`/api/reviews?freelancer_id=${freelancerId}&page=${page}&limit=${limit}`, "GET");
      console.log('Reviews API response:', response);
      
      if (response && response.data && Array.isArray(response.data)) {
        return response.data;
      } else {
        console.error('Unexpected response format from reviews API:', response);
        // Fallback aux données de mock
        return reviewsData.filter(r => r.freelancer_id === freelancerId);
      }
    } catch (error) {
      console.error(`Erreur lors de la récupération des reviews du freelancer ${freelancerId}:`, error);
      // Fallback aux données de mock
      return reviewsData.filter(r => r.freelancer_id === freelancerId);
    }
  }

  // Récupération des statistics pour l'analytics dashboard
  public async fetchAnalytics(
    filters?: Partial<AnalyticsFilter>
  ): Promise<FreelancerAnalytics> {
    try {
      // Construction de l'URL avec les filtres
      let endpoint = '/api/stats';
      
      if (filters) {
        const queryParams = [];
        
        if (filters.country) {
          queryParams.push(`country=${filters.country}`);
        }
        
        if (filters.skill) {
          queryParams.push(`skill=${filters.skill}`);
        }
        
        if (filters.source) {
          queryParams.push(`source=${filters.source}`);
        }
        
        if (filters.minRate !== undefined) {
          queryParams.push(`min_rate=${filters.minRate}`);
        }
        
        if (filters.maxRate !== undefined) {
          queryParams.push(`max_rate=${filters.maxRate}`);
        }
        
        if (filters.minRating !== undefined) {
          queryParams.push(`min_rating=${filters.minRating}`);
        }
        
        if (queryParams.length > 0) {
          endpoint += '?' + queryParams.join('&');
        }
      }
      
      // Récupération des statistiques complètes depuis le backend
      const stats = await api.fetchRequest(endpoint, "GET");
      
      // Conversion des données dans le format attendu par le frontend
      return {
        countryDistribution: stats.top_countries.map((item: any) => ({
          name: item.name,
          count: item.count
        })),
        skillDistribution: stats.top_skills.map((item: any) => ({
          name: item.name,
          count: item.count
        })),
        rateDistribution: stats.hourly_rate_distribution.map((item: any) => ({
          range: item.range,
          count: item.count
        })),
        signupsByMonth: stats.signup_by_month.map((item: any) => ({
          month: item.month,
          count: item.count
        })),
        sourceDistribution: stats.source_distribution.map((item: any) => ({
          source: item.source,
          count: item.count
        })),
        ratingDistribution: stats.rating_distribution.map((item: any) => ({
          rating: item.rating,
          count: item.count
        })),
        stats: {
          freelancersCount: stats.freelancers_count,
          countriesCount: stats.countries_count,
          servicesCount: stats.services_count,
          reviewsCount: stats.reviews_count,
          avgRating: stats.avg_rating,
          topCountries: stats.top_countries
        }
      };
    } catch (error) {
      console.error("Erreur lors de la récupération des analytics:", error);
      // Fallback aux données de mock
      console.warn("Utilisation des données de mock pour les analytics");
      
      // Simuler le même comportement qu'avant avec les données de mock
      let filteredData = [...freelancersData];
      
      if (filters) {
        if (filters.country) {
          filteredData = filteredData.filter(f => f.country_id === filters.country);
        }
        
        if (filters.skill) {
          filteredData = filteredData.filter(f => 
            f.main_skill === filters.skill || 
            f.skills?.includes(filters.skill as string)
          );
        }
        
        if (filters.minRate !== undefined) {
          filteredData = filteredData.filter(f => f.hourly_rate >= (filters.minRate as number));
        }
        
        if (filters.maxRate !== undefined) {
          filteredData = filteredData.filter(f => f.hourly_rate <= (filters.maxRate as number));
        }
        
        if (filters.source) {
          filteredData = filteredData.filter(f => f.source === filters.source);
        }
        
        if (filters.minRating !== undefined) {
          filteredData = filteredData.filter(f => f.rating >= (filters.minRating as number));
        }
      }
      
      // Ajout des pays aux freelancers
      const enrichedData = filteredData.map(freelancer => {
        const country = countriesData.find(c => c._id === freelancer.country_id);
        return { ...freelancer, country };
      });
      
      return {
        countryDistribution: this.calculateCountryDistribution(enrichedData),
        skillDistribution: this.calculateSkillDistribution(enrichedData),
        rateDistribution: this.calculateRateDistribution(enrichedData),
        signupsByMonth: this.calculateSignupsByMonth(enrichedData),
        sourceDistribution: this.calculateSourceDistribution(enrichedData),
        ratingDistribution: this.calculateRatingDistribution(enrichedData),
        stats: {
          freelancersCount: filteredData.length,
          countriesCount: countriesData.length,
          servicesCount: 0, // pas disponible dans les mocks
          reviewsCount: reviewsData.length,
          avgRating: filteredData.reduce((acc, curr) => acc + curr.rating, 0) / filteredData.length,
          topCountries: []
        }
      };
    }
  }

  // Récupération des reviews récentes
  public async fetchRecentReviews(
    limit = 10
  ): Promise<{ freelancer: Freelancer; review: Review }[]> {
    try {
      // Utiliser le paramètre include_freelancers pour récupérer les freelancers en une seule requête
      const response = await api.fetchRequest(`/api/reviews?limit=${limit}&include_freelancers=true`, "GET");
      const reviews = response.data;
      
      // Mapper les données pour correspondre au format attendu, en filtrant les entrées sans freelancer
      return reviews
        .filter((item: any) => item.freelancer) // Filtrer les items sans freelancer
        .map((item: any) => {
          // Extraire le freelancer avec toutes les propriétés requises
          const freelancer: Freelancer = {
            _id: item.freelancer._id,
            name: item.freelancer.name || 'Unknown Freelancer',
            country_id: item.freelancer.country_id || '',
            main_skill: item.freelancer.main_skill || '',
            hourly_rate: item.freelancer.hourly_rate || 0,
            min_price: item.freelancer.min_price || 0,
            max_price: item.freelancer.max_price || 0,
            created_at: item.freelancer.created_at || new Date().toISOString(),
            source: item.freelancer.source || '',
            rating: item.freelancer.rating || 0,
            reviews_count: item.freelancer.reviews_count || 0,
            skills: item.freelancer.skills || []
          };
          
          // Extraire la review avec toutes les propriétés requises
          const review: Review = {
            _id: item._id,
            freelancer_id: item.freelancer_id,
            title: item.title || '',
            text: item.text || 'No review text available',
            rating: item.rating || 0,
            created_at: item.created_at || new Date().toISOString()
          };
          
          return { freelancer, review };
        });
    } catch (error) {
      console.error("Erreur lors de la récupération des reviews récentes:", error);
      // Fallback aux données de mock
      console.warn("Utilisation des données de mock pour les reviews récentes");
      
      const sortedReviews = [...reviewsData]
        .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
        .slice(0, limit);
      
      return sortedReviews.map(review => {
        const freelancer = freelancersData.find(f => f._id === review.freelancer_id);
        if (!freelancer) {
          // Créer un freelancer par défaut si non trouvé
          const defaultFreelancer: Freelancer = {
            _id: review.freelancer_id,
            name: 'Unknown Freelancer',
            country_id: '',
            main_skill: '',
            hourly_rate: 0,
            min_price: 0,
            max_price: 0,
            created_at: new Date().toISOString(),
            source: '',
            rating: 0,
            reviews_count: 0,
            skills: []
          };
          
          return {
            freelancer: defaultFreelancer,
            review
          };
        }
        return {
          freelancer,
          review
        };
      });
    }
  }

  // Récupération des mots-clés des reviews
  public async fetchReviewKeywords(): Promise<{ word: string; count: number }[]> {
    // Cette fonctionnalité n'existe pas dans le backend, donc on utilise les données de mock
    await new Promise(resolve => setTimeout(resolve, 600));
    
    return [
      { word: 'Excellent', count: 78 },
      { word: 'Professional', count: 65 },
      { word: 'Amazing', count: 52 },
      { word: 'Responsive', count: 49 },
      { word: 'Quality', count: 45 },
      { word: 'Timely', count: 40 },
      { word: 'Creative', count: 38 },
      { word: 'Skilled', count: 35 },
      { word: 'Detailed', count: 32 },
      { word: 'Efficient', count: 30 },
      { word: 'Communication', count: 28 },
      { word: 'Experienced', count: 26 },
      { word: 'Talented', count: 24 },
      { word: 'Reliable', count: 22 },
      { word: 'Deadline', count: 20 },
      { word: 'Understanding', count: 18 },
      { word: 'Knowledgeable', count: 16 },
      { word: 'Collaborative', count: 14 },
      { word: 'Creative', count: 12 },
      { word: 'Helpful', count: 10 },
      { word: 'Organized', count: 8 },
      { word: 'Flexible', count: 8 },
      { word: 'Budget', count: 7 },
      { word: 'Friendly', count: 6 },
      { word: 'Innovative', count: 6 },
      { word: 'Detail-oriented', count: 5 },
      { word: 'Expert', count: 5 },
      { word: 'Patient', count: 4 },
      { word: 'Punctual', count: 4 },
      { word: 'Dedicated', count: 3 }
    ];
  }

  // Méthodes de traitement de données pour l'analytique - Utilisées uniquement en fallback
  private calculateCountryDistribution(data: Freelancer[]): { name: string; count: number }[] {
    const countriesCount = data.reduce((acc, curr) => {
      const countryName = curr.country?.name || 'Unknown';
      if (!acc[countryName]) {
        acc[countryName] = 0;
      }
      acc[countryName]++;
      return acc;
    }, {} as Record<string, number>);
    
    return Object.entries(countriesCount)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count);
  }
  
  private calculateSkillDistribution(data: Freelancer[]): { name: string; count: number }[] {
    const skillsCount = data.reduce((acc, curr) => {
      const skill = curr.main_skill || 'Unknown';
      if (!acc[skill]) {
        acc[skill] = 0;
      }
      acc[skill]++;
      return acc;
    }, {} as Record<string, number>);
    
    return Object.entries(skillsCount)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count);
  }
  
  private calculateRateDistribution(data: Freelancer[]): { range: string; count: number }[] {
    const ranges = [
      { min: 0, max: 20 },
      { min: 20, max: 40 },
      { min: 40, max: 60 },
      { min: 60, max: 80 },
      { min: 80, max: 100 },
      { min: 100, max: 150 },
      { min: 150, max: Infinity }
    ];
    
    const distribution = ranges.map(range => {
      const count = data.filter(f => 
        f.hourly_rate >= range.min && 
        f.hourly_rate < range.max
      ).length;
      
      return {
        range: range.max === Infinity ? `${range.min}+` : `${range.min}-${range.max}`,
        count
      };
    });
    
    return distribution.filter(item => item.count > 0);
  }
  
  private calculateSignupsByMonth(data: Freelancer[]): { month: string; count: number }[] {
    const signupsByMonth: Record<string, number> = {};
    
    data.forEach(freelancer => {
      const date = new Date(freelancer.created_at);
      const monthYear = `${date.getFullYear()}-${date.getMonth() + 1}`;
      
      if (!signupsByMonth[monthYear]) {
        signupsByMonth[monthYear] = 0;
      }
      
      signupsByMonth[monthYear]++;
    });
    
    return Object.entries(signupsByMonth)
      .map(([month, count]) => ({ month, count }))
      .sort((a, b) => a.month.localeCompare(b.month));
  }
  
  private calculateSourceDistribution(data: Freelancer[]): { source: string; count: number }[] {
    const sourcesCount = data.reduce((acc, curr) => {
      const source = curr.source || 'Unknown';
      if (!acc[source]) {
        acc[source] = 0;
      }
      acc[source]++;
      return acc;
    }, {} as Record<string, number>);
    
    return Object.entries(sourcesCount)
      .map(([source, count]) => ({ source, count }))
      .sort((a, b) => b.count - a.count);
  }
  
  private calculateRatingDistribution(data: Freelancer[]): { rating: number; count: number }[] {
    const ratings = [1, 2, 3, 4, 5];
    
    return ratings.map(rating => {
      // Count freelancers with this rounded rating
      const count = data.filter(f => {
        const roundedRating = Math.round(f.rating);
        return roundedRating === rating;
      }).length;
      
      return { rating, count };
    }).filter(item => item.count > 0);
  }

  // Récupération des compétences disponibles
  public async fetchSkills(): Promise<string[]> {
    try {
      const response = await api.fetchRequest('/api/skills', "GET");
      return response;
    } catch (error) {
      console.error("Erreur lors de la récupération des compétences:", error);
      // Fallback à une liste de compétences par défaut
      return [
        'JavaScript', 'React', 'Node.js', 'Python', 'Java', 'PHP', 
        'UI/UX Design', 'Graphic Design', 'Content Writing', 'SEO', 'Marketing'
      ];
    }
  }

  // Récupération des sources disponibles
  public async fetchSources(): Promise<string[]> {
    try {
      const response = await api.fetchRequest('/api/sources', "GET");
      return response;
    } catch (error) {
      console.error("Erreur lors de la récupération des sources:", error);
      // Fallback à une liste de sources par défaut
      return ['Freelancer', 'TrueLancer', 'PeoplePerHour', 'Upwork', 'Fiverr'];
    }
  }
}

export const jobService = new JobService(); 