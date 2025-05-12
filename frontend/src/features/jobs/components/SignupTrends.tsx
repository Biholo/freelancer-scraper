import React, { useRef, useEffect } from 'react';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

interface SignupData {
  month: string;
  count: number;
}

interface SignupTrendsProps {
  data: SignupData[];
}

const SignupTrends: React.FC<SignupTrendsProps> = ({ data }) => {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);

  useEffect(() => {
    if (!chartRef.current || !data?.length) return;

    // Destroy previous chart if it exists
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    // Sort data chronologically
    const sortedData = [...data].sort((a, b) => {
      const dateA = new Date(a.month);
      const dateB = new Date(b.month);
      return dateA.getTime() - dateB.getTime();
    });

    // Format dates to be more readable (e.g., "Jan 2023")
    const formattedLabels = sortedData.map(item => {
      const date = new Date(item.month);
      return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
    });

    const counts = sortedData.map(item => item.count);

    const ctx = chartRef.current.getContext('2d');
    if (!ctx) return;

    chartInstance.current = new Chart(ctx, {
      type: 'line',
      data: {
        labels: formattedLabels,
        datasets: [
          {
            label: 'New Freelancers',
            data: counts,
            borderColor: 'rgba(153, 102, 255, 1)',
            backgroundColor: 'rgba(153, 102, 255, 0.2)',
            borderWidth: 2,
            fill: true,
            tension: 0.4,
            pointRadius: 3,
            pointBackgroundColor: 'rgba(153, 102, 255, 1)',
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
                return `New freelancers: ${context.raw}`;
              },
            },
          },
        },
        scales: {
          x: {
            grid: {
              display: false,
            },
            title: {
              display: true,
              text: 'Month',
              font: {
                size: 12,
              },
            },
          },
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'New Freelancers',
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
    return <div className="text-center text-gray-500 py-8">No signup trend data available</div>;
  }

  return (
    <div className="h-[300px]">
      <canvas ref={chartRef} />
    </div>
  );
};

export default SignupTrends; 