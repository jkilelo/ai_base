import React from 'react';
import { Card, Badge } from 'react-bootstrap';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

interface StatCardProps {
  title: string;
  value: string | number;
  change?: number;
  changeType?: 'increase' | 'decrease' | 'neutral';
  icon?: React.ReactNode;
  color?: 'primary' | 'success' | 'warning' | 'danger' | 'info';
  loading?: boolean;
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  change,
  changeType = 'neutral',
  icon,
  color = 'primary',
  loading = false
}) => {
  const { isDark } = useTheme();

  const getTrendIcon = () => {
    switch (changeType) {
      case 'increase':
        return <TrendingUp size={16} className="text-success" />;
      case 'decrease':
        return <TrendingDown size={16} className="text-danger" />;
      default:
        return <Minus size={16} className="text-muted" />;
    }
  };

  const getChangeColor = () => {
    switch (changeType) {
      case 'increase':
        return 'success';
      case 'decrease':
        return 'danger';
      default:
        return 'secondary';
    }
  };

  return (
    <Card className={`stat-card h-100 ${isDark ? 'dark' : ''}`}>
      <Card.Body>
        <div className="d-flex justify-content-between align-items-start mb-3">
          <div>
            <h6 className={`card-title mb-0 ${isDark ? 'text-light' : 'text-muted'}`}>
              {title}
            </h6>
          </div>
          {icon && (
            <div className={`text-${color}`}>
              {icon}
            </div>
          )}
        </div>
        
        <div className="mb-2">
          {loading ? (
            <div className="placeholder-glow">
              <span className="placeholder col-6"></span>
            </div>
          ) : (
            <h3 className={`mb-0 fw-bold ${isDark ? 'text-light' : 'text-dark'}`}>
              {value}
            </h3>
          )}
        </div>

        {change !== undefined && !loading && (
          <div className="d-flex align-items-center">
            {getTrendIcon()}
            <Badge bg={getChangeColor()} className="ms-2">
              {change > 0 ? '+' : ''}{change}%
            </Badge>
          </div>
        )}
      </Card.Body>
    </Card>
  );
};

export default StatCard;
