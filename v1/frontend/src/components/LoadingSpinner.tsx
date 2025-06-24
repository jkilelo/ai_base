import React from 'react';
import { Card, Spinner } from 'react-bootstrap';
import { useTheme } from '../contexts/ThemeContext';

interface LoadingSpinnerProps {
  size?: 'sm' | 'lg';
  text?: string;
  overlay?: boolean;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'lg', 
  text = 'Loading...', 
  overlay = false 
}) => {
  const { isDark } = useTheme();

  const content = (
    <div className="d-flex flex-column align-items-center justify-content-center p-4">      <Spinner 
        animation="border" 
        variant={isDark ? 'light' : 'primary'} 
        size={size === 'sm' ? 'sm' : undefined}
        className="mb-3"
      />
      <span className={isDark ? 'text-light' : 'text-muted'}>{text}</span>
    </div>
  );

  if (overlay) {
    return (
      <div 
        className="position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center loading-overlay"
      >
        <Card className={`text-center ${isDark ? 'bg-dark text-light' : 'bg-light'}`}>
          <Card.Body>
            {content}
          </Card.Body>
        </Card>
      </div>
    );
  }

  return content;
};

export default LoadingSpinner;
