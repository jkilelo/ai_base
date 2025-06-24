import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Alert, Button } from 'react-bootstrap';
import { Activity, Database, Server, Clock } from 'lucide-react';
import StatCard from '../StatCard';
import LoadingSpinner from '../LoadingSpinner';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { healthApi } from '../../services/api';
import { useTheme } from '../../contexts/ThemeContext';
import { useNotifications } from '../../contexts/NotificationContext';

const DashboardOverview: React.FC = () => {
  const { isDark } = useTheme();
  const { addNotification } = useNotifications();
  const [loading, setLoading] = useState(true);
  const [healthData, setHealthData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // Mock chart data for demonstration
  const responseTimeData = [
    { time: '00:00', value: 45 },
    { time: '04:00', value: 52 },
    { time: '08:00', value: 38 },
    { time: '12:00', value: 61 },
    { time: '16:00', value: 42 },
    { time: '20:00', value: 55 },
  ];

  const requestsData = [
    { time: '00:00', requests: 120 },
    { time: '04:00', requests: 89 },
    { time: '08:00', requests: 245 },
    { time: '12:00', requests: 320 },
    { time: '16:00', requests: 278 },
    { time: '20:00', requests: 156 },
  ];

  const fetchHealthData = async () => {
    try {
      setLoading(true);
      const data = await healthApi.getAllHealth();
      setHealthData(data);
      setError(null);
      setLastUpdate(new Date());

      // Check for any issues and notify
      if (data.errors.health || data.errors.database || data.errors.system) {
        addNotification({
          type: 'warning',
          title: 'Health Check Issues',
          message: 'Some health endpoints are experiencing issues.'
        });
      } else {
        addNotification({
          type: 'success',
          title: 'Health Check Complete',
          message: 'All systems are operational.'
        });
      }
    } catch (err) {
      setError('Failed to fetch health data');
      addNotification({
        type: 'error',
        title: 'Connection Error',
        message: 'Unable to connect to the API server.'
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealthData();
    const interval = setInterval(fetchHealthData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
      case 'ok':
        return 'success';
      case 'unhealthy':
      case 'error':
        return 'danger';
      default:
        return 'warning';
    }
  };

  if (loading && !healthData) {
    return <LoadingSpinner text="Loading dashboard data..." />;
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className={isDark ? 'text-light' : 'text-dark'}>Dashboard Overview</h2>
          <p className={`mb-0 ${isDark ? 'text-light' : 'text-muted'}`}>
            Real-time monitoring of your FastAPI application
          </p>
        </div>
        <div className="d-flex align-items-center">
          <small className={`me-3 ${isDark ? 'text-light' : 'text-muted'}`}>
            Last updated: {lastUpdate.toLocaleTimeString()}
          </small>
          <Button 
            variant="outline-primary" 
            size="sm" 
            onClick={fetchHealthData}
            disabled={loading}
          >
            {loading ? 'Refreshing...' : 'Refresh'}
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="danger" className="mb-4">
          <strong>Error:</strong> {error}
        </Alert>
      )}

      {/* Status Cards */}
      <Row className="mb-4">
        <Col md={3}>
          <StatCard
            title="API Status"
            value={healthData?.health?.status || 'Unknown'}
            icon={<Activity size={24} />}
            color={getStatusColor(healthData?.health?.status)}
            loading={loading}
          />
        </Col>
        <Col md={3}>
          <StatCard
            title="Database"
            value={healthData?.database?.database_status || 'Unknown'}
            icon={<Database size={24} />}
            color={getStatusColor(healthData?.database?.database_status)}
            loading={loading}
          />
        </Col>
        <Col md={3}>
          <StatCard
            title="System"
            value={healthData?.system?.status || 'Unknown'}
            icon={<Server size={24} />}
            color={getStatusColor(healthData?.system?.status)}
            loading={loading}
          />
        </Col>
        <Col md={3}>
          <StatCard
            title="Uptime"
            value={healthData?.system?.uptime || 'N/A'}
            icon={<Clock size={24} />}
            color="info"
            loading={loading}
          />
        </Col>
      </Row>

      {/* Charts */}
      <Row className="mb-4">
        <Col lg={6}>
          <Card className={`chart-container h-100 ${isDark ? 'dark' : ''}`}>
            <Card.Header>
              <h5 className={`mb-0 ${isDark ? 'text-light' : 'text-dark'}`}>
                Response Time (ms)
              </h5>
            </Card.Header>
            <Card.Body>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={responseTimeData}>
                  <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#495057' : '#e9ecef'} />
                  <XAxis dataKey="time" stroke={isDark ? '#f8f9fa' : '#6c757d'} />
                  <YAxis stroke={isDark ? '#f8f9fa' : '#6c757d'} />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: isDark ? '#495057' : '#fff',
                      border: `1px solid ${isDark ? '#6c757d' : '#dee2e6'}`,
                      color: isDark ? '#f8f9fa' : '#212529'
                    }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="value" 
                    stroke="#667eea" 
                    strokeWidth={2}
                    dot={{ fill: '#667eea', strokeWidth: 2, r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={6}>
          <Card className={`chart-container h-100 ${isDark ? 'dark' : ''}`}>
            <Card.Header>
              <h5 className={`mb-0 ${isDark ? 'text-light' : 'text-dark'}`}>
                Requests per Hour
              </h5>
            </Card.Header>
            <Card.Body>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={requestsData}>
                  <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#495057' : '#e9ecef'} />
                  <XAxis dataKey="time" stroke={isDark ? '#f8f9fa' : '#6c757d'} />
                  <YAxis stroke={isDark ? '#f8f9fa' : '#6c757d'} />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: isDark ? '#495057' : '#fff',
                      border: `1px solid ${isDark ? '#6c757d' : '#dee2e6'}`,
                      color: isDark ? '#f8f9fa' : '#212529'
                    }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="requests" 
                    stroke="#28a745" 
                    fill="#28a745" 
                    fillOpacity={0.3}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* System Information */}
      <Row>
        <Col lg={8}>
          <Card className={`${isDark ? 'bg-dark text-light' : 'bg-light'} h-100`}>
            <Card.Header>
              <h5 className="mb-0">System Information</h5>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <div className="mb-3">
                    <strong>Environment:</strong> {healthData?.system?.environment || 'N/A'}
                  </div>
                  <div className="mb-3">
                    <strong>Version:</strong> {healthData?.system?.version || 'N/A'}
                  </div>
                </Col>
                <Col md={6}>
                  <div className="mb-3">
                    <strong>Database Driver:</strong> {healthData?.database?.connection_details?.driver || 'N/A'}
                  </div>
                  <div className="mb-3">
                    <strong>Database Name:</strong> {healthData?.database?.connection_details?.database || 'N/A'}
                  </div>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={4}>
          <Card className={`${isDark ? 'bg-dark text-light' : 'bg-light'} h-100`}>
            <Card.Header>
              <h5 className="mb-0">Quick Actions</h5>
            </Card.Header>
            <Card.Body className="d-flex flex-column">
              <Button variant="outline-primary" className="mb-2">
                View API Documentation
              </Button>
              <Button variant="outline-success" className="mb-2">
                Run Health Check
              </Button>
              <Button variant="outline-info" className="mb-2">
                View System Logs
              </Button>
              <Button variant="outline-warning" className="mt-auto">
                System Settings
              </Button>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default DashboardOverview;
