import React, { useRef, useEffect } from 'react';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

interface RateData {
  range: string;
  count: number;
}

interface RateAnalysisProps {
  data: RateData[];
}

const RateAnalysis: React.FC<RateAnalysisProps> = ({ data }) => {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);

  useEffect(() => {
    if (!chartRef.current || !data?.length) return;

    // Destroy previous chart if it exists
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    // Ensure data is sorted by rate ranges (assuming they're formatted like "0-10", "10-20", etc.)
    const sortedData = [...data].sort((a, b) => {
      const aStart = parseInt(a.range.split('-')[0]);
      const bStart = parseInt(b.range.split('-')[0]);
      return aStart - bStart;
    });

    const labels = sortedData.map(item => item.range);
    const counts = sortedData.map(item => item.count);

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
            backgroundColor: 'rgba(75, 192, 192, 0.8)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1,
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
              text: 'Hourly Rate Range ($)',
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
    return <div className="text-center text-gray-500 py-8">No rate data available</div>;
  }

  return (
    <div className="h-[300px]">
      <canvas ref={chartRef} />
    </div>
  );
};

export default RateAnalysis; 