import React from 'react';
import { useReviewKeywords } from '@/api/queries/jobQueries';
import Loader from '@/components/ui/Loader';

interface WordCloudItemProps {
  word: string;
  count: number;
  max: number;
}

const WordCloudItem: React.FC<WordCloudItemProps> = ({ word, count, max }) => {
  // Calculate font size based on count relative to max (between 0.8 and 2.5rem)
  const fontSize = 0.8 + ((count / max) * 1.7);
  
  // Generate a color based on count (darker for higher counts)
  const colorIntensity = Math.floor(40 + ((count / max) * 60));
  const color = `rgba(79, 70, 229, ${colorIntensity / 100})`;
  
  return (
    <span 
      className="inline-block m-1 px-2 py-1 rounded-md"
      style={{ 
        fontSize: `${fontSize}rem`,
        color: color,
        fontWeight: count > (max / 2) ? 'bold' : 'normal'
      }}
    >
      {word}
    </span>
  );
};

const ReviewKeywords: React.FC = () => {
  const { data: keywords, isLoading, error } = useReviewKeywords();

  if (isLoading) return <Loader />;
  
  if (error) return <div className="text-red-500">Error loading keywords</div>;
  
  if (!keywords || keywords.length === 0) {
    return <div className="text-center text-gray-500 py-8">No keyword data available</div>;
  }

  // Find the maximum count for scaling
  const maxCount = Math.max(...keywords.map(item => item.count));

  return (
    <div className="text-center p-2">
      {keywords.map((item, index) => (
        <WordCloudItem 
          key={index} 
          word={item.word} 
          count={item.count} 
          max={maxCount}
        />
      ))}
    </div>
  );
};

export default ReviewKeywords; 