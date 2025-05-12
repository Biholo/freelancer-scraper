import React, { useRef, useEffect } from 'react';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

interface CountryData {
  name: string;
  count: number;
}

interface CountryDistributionProps {
  data: CountryData[];
}

const CountryDistribution: React.FC<CountryDistributionProps> = ({ data }) => {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);

  useEffect(() => {
    if (!chartRef.current || !data?.length) return;

    // Destroy previous chart if it exists
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    // Sort data by count (descending)
    const sortedData = [...data].sort((a, b) => b.count - a.count);
    
    // Limit to top 10 countries (for readability)
    const displayData = sortedData.slice(0, 10);
    
    const labels = displayData.map(item => item.name);
    const counts = displayData.map(item => item.count);
    
    // Generate colors - different shade of blue for each segment
    const generateColors = (count: number) => {
      return Array(count).fill(0).map((_, i) => 
        `hsl(210, 70%, ${60 - (i * 3)}%)`
      );
    };

    const ctx = chartRef.current.getContext('2d');
    if (!ctx) return;

    chartInstance.current = new Chart(ctx, {
      type: 'pie',
      data: {
        labels,
        datasets: [
          {
            data: counts,
            backgroundColor: generateColors(labels.length),
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
            position: 'right',
            labels: {
              boxWidth: 15,
              font: {
                size: 11,
              },
            },
          },
          tooltip: {
            callbacks: {
              label: (context) => {
                const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
                const value = context.raw as number;
                const percentage = Math.round((value / total) * 100);
                return `${context.label}: ${value} (${percentage}%)`;
              },
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
    return <div className="text-center text-gray-500 py-8">No country data available</div>;
  }

  return (
    <div className="h-[300px]">
      <canvas ref={chartRef} />
    </div>
  );
};

export default CountryDistribution; 