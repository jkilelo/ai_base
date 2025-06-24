import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Alert, Button } from 'react-bootstrap';
import { RefreshCw } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { useNotifications } from '../contexts/NotificationContext';
import { healthApi } from '../services/api';
import StatsGrid from './StatsGrid';
import ChartsGrid from './ChartsGrid';
import LoadingSpinner from './LoadingSpinner';

const Dashboard: React.FC = () => {
  const { isDark } = useTheme();
  const { addNotification } = useNotifications();
  const [healthData, setHealthData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const fetchHealthData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await healthApi.getAllHealth();
      setHealthData(data);
      setLastUpdate(new Date());
      
      // Check for any errors and add notifications
      if (data.errors.health) {
        addNotification({
          type: 'error',
          title: 'API Health Check Failed',
          message: 'Unable to connect to FastAPI backend'
        });
      }
      
      if (data.errors.database) {
        addNotification({
          type: 'warning',
          title: 'Database Check Warning',
          message: 'Database health endpoint not responding'
        });
      }
      
      if (data.errors.system) {
        addNotification({
          type: 'warning',
          title: 'System Check Warning',
          message: 'System health endpoint not responding'
        });
      }
      
      // Success notification for first successful load
      if (!data.errors.health && !healthData) {
        addNotification({
          type: 'success',
          title: 'Connected to Backend',
          message: 'Successfully connected to FastAPI server'
        });
      }
      
    } catch (err) {
      const errorMessage = 'Failed to fetch health data. Make sure the FastAPI backend is running on http://localhost:8000';
      setError(errorMessage);
      addNotification({
        type: 'error',
        title: 'Connection Error',
        message: errorMessage
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealthData();
    
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(fetchHealthData, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    fetchHealthData();
    addNotification({
      type: 'info',
      title: 'Refreshing Data',
      message: 'Updating dashboard information...'
    });
  };

  if (loading && !healthData) {
    return (
      <Container fluid className="py-4">
        <LoadingSpinner text="Loading dashboard data..." />
      </Container>
    );
  }

  return (
    <Container fluid className="py-4">
      {/* Header */}
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h2 className={isDark ? 'text-light' : 'text-dark'}>
                Dashboard Overview
              </h2>
              <p className={`mb-0 ${isDark ? 'text-light' : 'text-muted'}`}>
                Real-time monitoring of your FastAPI application
              </p>
            </div>
            <div className="d-flex align-items-center gap-3">
              {lastUpdate && (
                <small className={isDark ? 'text-light' : 'text-muted'}>
                  Last updated: {lastUpdate.toLocaleTimeString()}
                </small>
              )}
              <Button 
                variant="outline-primary" 
                size="sm" 
                onClick={handleRefresh}
                disabled={loading}
                className="d-flex align-items-center gap-2"
              >
                <RefreshCw size={16} className={loading ? 'rotating' : ''} />
                Refresh
              </Button>
            </div>
          </div>
        </Col>
      </Row>

      {/* Error Alert */}
      {error && (
        <Alert variant="danger" className="mb-4" dismissible onClose={() => setError(null)}>
          <Alert.Heading>Connection Error</Alert.Heading>
          <p className="mb-2">{error}</p>
          <hr />
          <div className="mb-0">
            <strong>Troubleshooting:</strong>
            <ul className="mb-0 mt-2">
              <li>Make sure the FastAPI backend is running: <code>cd ../backend && .\start_backend.bat</code></li>
              <li>Check that the backend is accessible at: <a href="http://localhost:8000" target="_blank" rel="noopener noreferrer">http://localhost:8000</a></li>
              <li>Verify the API documentation at: <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">http://localhost:8000/docs</a></li>
            </ul>
          </div>
        </Alert>
      )}

      {/* Stats Grid */}
      <StatsGrid healthData={healthData} loading={loading} />

      {/* Charts Grid */}
      <ChartsGrid healthData={healthData} />
    </Container>
  );
};

export default Dashboard;
