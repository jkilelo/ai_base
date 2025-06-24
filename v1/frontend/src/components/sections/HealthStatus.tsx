import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Badge, Alert, Button, Spinner } from 'react-bootstrap';
import { Activity, CheckCircle, XCircle, AlertTriangle, RefreshCw } from 'lucide-react';
import { healthApi } from '../../services/api';
import { useTheme } from '../../contexts/ThemeContext';
import { useNotifications } from '../../contexts/NotificationContext';

const HealthStatus: React.FC = () => {
  const { isDark } = useTheme();
  const { addNotification } = useNotifications();
  const [healthData, setHealthData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  const fetchHealthData = async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      
      const data = await healthApi.getAllHealth();
      setHealthData(data);
      setLastUpdate(new Date());

      if (isRefresh) {
        addNotification({
          type: 'success',
          title: 'Health Status Updated',
          message: 'All health checks have been refreshed.'
        });
      }
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Health Check Failed',
        message: 'Unable to fetch health status from the server.'
      });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchHealthData();
    const interval = setInterval(() => fetchHealthData(), 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
      case 'ok':
        return <CheckCircle className="text-success" size={20} />;
      case 'unhealthy':
      case 'error':
        return <XCircle className="text-danger" size={20} />;
      default:
        return <AlertTriangle className="text-warning" size={20} />;
    }
  };

  const getStatusVariant = (status: string) => {
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

  const healthChecks = [
    {
      name: 'API Health',
      status: healthData?.health?.status,
      message: healthData?.health?.message,
      timestamp: healthData?.health?.timestamp,
      error: healthData?.errors?.health,
      details: healthData?.health?.details
    },
    {
      name: 'Database Connection',
      status: healthData?.database?.database_status,
      message: healthData?.database?.message,
      timestamp: healthData?.database?.timestamp,
      error: healthData?.errors?.database,
      details: healthData?.database?.connection_details
    },
    {
      name: 'System Status',
      status: healthData?.system?.status,
      message: healthData?.system?.message,
      timestamp: healthData?.system?.timestamp,
      error: healthData?.errors?.system,
      details: {
        uptime: healthData?.system?.uptime,
        version: healthData?.system?.version,
        environment: healthData?.system?.environment
      }
    }
  ];
  if (loading && !healthData) {
    return (
      <div className="d-flex justify-content-center align-items-center loading-container">
        <div className="text-center">
          <Spinner animation="border" variant="primary" className="mb-3" />
          <p className={isDark ? 'text-light' : 'text-muted'}>Loading health status...</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className={isDark ? 'text-light' : 'text-dark'}>Health Status</h2>
          <p className={`mb-0 ${isDark ? 'text-light' : 'text-muted'}`}>
            Monitor the health of all system components
          </p>
        </div>
        <div className="d-flex align-items-center">
          <small className={`me-3 ${isDark ? 'text-light' : 'text-muted'}`}>
            Last checked: {lastUpdate.toLocaleTimeString()}
          </small>
          <Button 
            variant="outline-primary" 
            size="sm" 
            onClick={() => fetchHealthData(true)}
            disabled={refreshing}
          >
            {refreshing ? (
              <>
                <Spinner animation="border" size="sm" className="me-2" />
                Refreshing...
              </>
            ) : (
              <>
                <RefreshCw size={16} className="me-2" />
                Refresh
              </>
            )}
          </Button>
        </div>
      </div>

      <Row>
        {healthChecks.map((check, index) => (
          <Col lg={4} md={6} key={index} className="mb-4">
            <Card className={`h-100 ${isDark ? 'bg-dark text-light' : 'bg-light'}`}>
              <Card.Header className="d-flex justify-content-between align-items-center">
                <div className="d-flex align-items-center">
                  <Activity size={18} className="me-2" />
                  <h6 className="mb-0">{check.name}</h6>
                </div>
                {check.status && getStatusIcon(check.status)}
              </Card.Header>
              <Card.Body>
                {check.error ? (
                  <Alert variant="danger">
                    <strong>Error:</strong> {check.error.message || 'Unable to connect'}
                  </Alert>
                ) : (
                  <>
                    <div className="mb-3">
                      <Badge 
                        bg={getStatusVariant(check.status || 'unknown')} 
                        className="mb-2"
                      >
                        {check.status || 'Unknown'}
                      </Badge>
                      {check.message && (
                        <p className="mb-0 small">{check.message}</p>
                      )}
                    </div>                    {check.details && (
                      <div className="border-top pt-3">
                        <h6 className="small text-muted mb-2">Details:</h6>
                        {Object.entries(check.details).filter(([_, value]) => value).map(([key, value]) => (
                          <div key={key} className="d-flex justify-content-between small mb-1">
                            <span className="text-muted">{key.replace('_', ' ')}:</span>
                            <span>{String(value)}</span>
                          </div>
                        ))}
                      </div>
                    )}

                    {check.timestamp && (
                      <div className="border-top pt-2 mt-2">
                        <small className="text-muted">
                          Last checked: {new Date(check.timestamp).toLocaleString()}
                        </small>
                      </div>
                    )}
                  </>
                )}
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Overall Status Summary */}
      <Row className="mt-4">
        <Col>
          <Card className={`${isDark ? 'bg-dark text-light' : 'bg-light'}`}>
            <Card.Header>
              <h5 className="mb-0">System Health Summary</h5>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={8}>
                  <div className="mb-3">
                    {healthChecks.every(check => !check.error && (check.status === 'healthy' || check.status === 'ok')) ? (
                      <Alert variant="success" className="mb-0">
                        <CheckCircle size={20} className="me-2" />
                        All systems are operational and healthy.
                      </Alert>
                    ) : healthChecks.some(check => check.error || check.status === 'unhealthy') ? (
                      <Alert variant="danger" className="mb-0">
                        <XCircle size={20} className="me-2" />
                        One or more systems are experiencing issues that require attention.
                      </Alert>
                    ) : (
                      <Alert variant="warning" className="mb-0">
                        <AlertTriangle size={20} className="me-2" />
                        System status is partially unknown or degraded.
                      </Alert>
                    )}
                  </div>
                </Col>
                <Col md={4} className="text-end">
                  <div className="d-grid gap-2">
                    <Button variant="outline-primary" size="sm">
                      View Detailed Logs
                    </Button>
                    <Button variant="outline-secondary" size="sm">
                      Export Health Report
                    </Button>
                  </div>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default HealthStatus;
