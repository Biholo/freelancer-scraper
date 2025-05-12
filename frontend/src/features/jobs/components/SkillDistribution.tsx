import React, { useRef, useEffect } from 'react';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

interface SkillData {
  name: string;
  count: number;
}

interface SkillDistributionProps {
  data: SkillData[];
}

const SkillDistribution: React.FC<SkillDistributionProps> = ({ data }) => {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);

  useEffect(() => {
    if (!chartRef.current || !data?.length) return;

    // Destroy previous chart if it exists
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    // Sort data by count (descending) and get top 10
    const sortedData = [...data]
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);

    const labels = sortedData.map(item => item.name);
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
            backgroundColor: 'rgba(54, 162, 235, 0.8)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y', // Horizontal bar chart
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
          y: {
            ticks: {
              font: {
                size: 11,
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
    return <div className="text-center text-gray-500 py-8">No skill data available</div>;
  }

  return (
    <div className="h-[300px]">
      <canvas ref={chartRef} />
    </div>
  );
};

export default SkillDistribution; 