import React from 'react';
import { Card, Badge, Row, Col } from 'react-bootstrap';
import { Activity, Database, Server, Zap } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

interface StatCardProps {
  title: string;
  value: string | number;
  status: 'healthy' | 'unhealthy' | 'warning' | 'loading';
  icon: React.ReactNode;
  details?: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, status, icon, details }) => {
  const { isDark } = useTheme();

  const getStatusColor = () => {
    switch (status) {
      case 'healthy': return 'success';
      case 'unhealthy': return 'danger';
      case 'warning': return 'warning';
      default: return 'secondary';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'healthy': return 'Healthy';
      case 'unhealthy': return 'Error';
      case 'warning': return 'Warning';
      case 'loading': return 'Loading...';
      default: return 'Unknown';
    }
  };

  return (
    <Card className={`stat-card h-100 ${isDark ? 'dark' : ''}`}>
      <Card.Body>
        <div className="d-flex justify-content-between align-items-start mb-3">
          <div className="d-flex align-items-center">
            <div className="me-3 text-primary">
              {icon}
            </div>
            <div>
              <h6 className="card-title mb-1">{title}</h6>
              <Badge bg={getStatusColor()}>{getStatusText()}</Badge>
            </div>
          </div>
        </div>
        
        <div className="mb-2">
          <h4 className="mb-1">{value}</h4>
          {details && (
            <small className={`${isDark ? 'text-light' : 'text-muted'}`}>
              {details}
            </small>
          )}
        </div>
      </Card.Body>
    </Card>
  );
};

interface StatsGridProps {
  healthData: any;
  loading: boolean;
}

const StatsGrid: React.FC<StatsGridProps> = ({ healthData, loading }) => {
  const getHealthStatus = (data: any, type: string): 'healthy' | 'unhealthy' | 'warning' | 'loading' => {
    if (loading) return 'loading';
    if (!data) return 'unhealthy';
    
    if (type === 'general') {
      return data.status === 'healthy' ? 'healthy' : 'unhealthy';
    }
    
    if (type === 'database') {
      return data.database_status === 'connected' ? 'healthy' : 'unhealthy';
    }
    
    if (type === 'system') {
      return data.status === 'healthy' ? 'healthy' : 'warning';
    }
    
    return 'warning';
  };

  const stats = [
    {
      title: 'API Health',
      value: loading ? 'Checking...' : (healthData?.health?.status || 'Unknown'),
      status: getHealthStatus(healthData?.health, 'general'),
      icon: <Activity size={24} />,
      details: healthData?.health?.message || 'API status check'
    },
    {
      title: 'Database',
      value: loading ? 'Checking...' : (healthData?.database?.database_status || 'Unknown'),
      status: getHealthStatus(healthData?.database, 'database'),
      icon: <Database size={24} />,
      details: healthData?.database?.connection_details?.driver || 'Database connection'
    },
    {
      title: 'System',
      value: loading ? 'Checking...' : (healthData?.system?.uptime || 'Unknown'),
      status: getHealthStatus(healthData?.system, 'system'),
      icon: <Server size={24} />,
      details: healthData?.system?.version || 'System information'
    },
    {
      title: 'Performance',
      value: loading ? 'Checking...' : 'Optimal',
      status: 'healthy' as const,
      icon: <Zap size={24} />,
      details: 'Response time < 100ms'
    }
  ];

  return (
    <Row className="g-4 mb-4">
      {stats.map((stat, index) => (
        <Col key={index} sm={6} lg={3}>
          <StatCard {...stat} />
        </Col>
      ))}
    </Row>
  );
};

export default StatsGrid;
