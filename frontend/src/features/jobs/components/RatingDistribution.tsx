import React, { useRef, useEffect } from 'react';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

interface RatingData {
  rating: number;
  count: number;
}

interface RatingDistributionProps {
  data: RatingData[];
}

const RatingDistribution: React.FC<RatingDistributionProps> = ({ data }) => {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);

  useEffect(() => {
    if (!chartRef.current || !data?.length) return;

    // Destroy previous chart if it exists
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    // Sort data by rating
    const sortedData = [...data].sort((a, b) => a.rating - b.rating);
    
    const labels = sortedData.map(item => `${item.rating} Star${item.rating !== 1 ? 's' : ''}`);
    const counts = sortedData.map(item => item.count);
    
    const generateColors = () => {
      // Use a color gradient from red to green for ratings
      return sortedData.map(item => {
        // Calculate a color based on rating (1 = red, 5 = green)
        const normalized = (item.rating - 1) / 4; // normalize to 0-1
        const r = Math.round(255 * (1 - normalized));
        const g = Math.round(255 * normalized);
        const b = 0;
        return `rgba(${r}, ${g}, ${b}, 0.8)`;
      });
    };

    const ctx = chartRef.current.getContext('2d');
    if (!ctx) return;

    chartInstance.current = new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [
          {
            label: 'Number of Freelancers',
            data: counts,
            backgroundColor: generateColors(),
            borderWidth: 1,
            borderColor: '#fff',
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            callbacks: {
              label: (context) => {
                return `Freelancers: ${context.raw}`;
              },
            },
          },
        },
        scales: {
          x: {
            title: {
              display: true,
              text: 'Rating',
              font: {
                size: 12,
              },
            },
          },
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Number of Freelancers',
              font: {
                size: 12,
              },
            },
            ticks: {
              precision: 0,
            },
          },
        },
      },
    });

    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
        chartInstance.current = null;
      }
    };
  }, [data]);

  if (!data || data.length === 0) {
    return <div className="text-center text-gray-500 py-8">No rating data available</div>;
  }

  return (
    <div className="h-[300px]">
      <canvas ref={chartRef} />
    </div>
  );
};

export default RatingDistribution; 