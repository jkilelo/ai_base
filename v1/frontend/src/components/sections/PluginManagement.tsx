import React, { useState, useEffect } from 'react';
import { Card, Table, Badge, Button, Modal, Spinner, Alert } from 'react-bootstrap';
import { useTheme } from '../../contexts/ThemeContext';
import { useNotifications } from '../../contexts/NotificationContext';
import axios from 'axios';
import { Plug, Info, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';

interface Plugin {
  name: string;
  version: string;
  description: string;
  status: string;
  author: string;
  dependencies: string[];
}

interface PluginResponse {
  plugins: Record<string, Plugin>;
  total: number;
}

const PluginManagement: React.FC = () => {
  const { isDark } = useTheme();
  const { addNotification } = useNotifications();
  const [plugins, setPlugins] = useState<Record<string, Plugin>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [selectedPlugin, setSelectedPlugin] = useState<string | null>(null);
  const [pluginDetails, setPluginDetails] = useState<any>(null);

  const api = axios.create({
    baseURL: 'http://localhost:8001',
    timeout: 10000,
  });

  useEffect(() => {
    fetchPlugins();
  }, []);

  const fetchPlugins = async () => {
    try {
      setLoading(true);
      const response = await api.get<PluginResponse>('/api/v1/plugins');
      setPlugins(response.data.plugins);
      setError(null);
    } catch (err) {
      setError('Failed to fetch plugins');
      addNotification({
        type: 'error',
        title: 'Error',
        message: 'Failed to fetch plugins'
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchPluginDetails = async (pluginName: string) => {
    try {
      const response = await api.get(`/api/v1/plugins/${pluginName}/info`);
      setPluginDetails(response.data);
      setSelectedPlugin(pluginName);
      setShowModal(true);
    } catch (err) {
      addNotification({
        type: 'error',
        title: 'Error',
        message: `Failed to fetch details for ${pluginName}`
      });
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return <CheckCircle size={16} className="text-success" />;
      case 'inactive':
        return <XCircle size={16} className="text-danger" />;
      case 'error':
        return <AlertTriangle size={16} className="text-warning" />;
      default:
        return <AlertTriangle size={16} className="text-muted" />;
    }
  };

  const getStatusVariant = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'success';
      case 'inactive':
        return 'secondary';
      case 'error':
        return 'warning';
      default:
        return 'secondary';
    }
  };

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center min-vh-25">
        <Spinner animation="border" variant={isDark ? 'light' : 'primary'} />
        <span className={`ms-2 ${isDark ? 'text-light' : 'text-dark'}`}>Loading plugins...</span>
      </div>
    );
  }

  return (
    <div className={`p-4 ${isDark ? 'text-light' : 'text-dark'}`}>
      <div className="d-flex align-items-center mb-4">
        <Plug size={24} className="me-2" />
        <h2 className="mb-0">Plugin Management</h2>
      </div>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Card className={isDark ? 'bg-dark border-secondary' : ''}>
        <Card.Header className={`d-flex justify-content-between align-items-center ${isDark ? 'bg-dark border-secondary text-light' : ''}`}>
          <h5 className="mb-0">Installed Plugins ({Object.keys(plugins).length})</h5>
          <Button variant="outline-primary" size="sm" onClick={fetchPlugins}>
            Refresh
          </Button>
        </Card.Header>
        <Card.Body className={isDark ? 'bg-dark text-light' : ''}>
          {Object.keys(plugins).length === 0 ? (
            <div className="text-center py-4">
              <Plug size={48} className="text-muted mb-3" />
              <p className="text-muted">No plugins installed</p>
            </div>
          ) : (
            <Table responsive className={isDark ? 'table-dark' : ''}>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Version</th>
                  <th>Description</th>
                  <th>Status</th>
                  <th>Author</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(plugins).map(([key, plugin]) => (
                  <tr key={key}>
                    <td className="fw-bold">{plugin.name}</td>
                    <td>
                      <Badge bg="info">{plugin.version}</Badge>
                    </td>
                    <td className="text-muted">{plugin.description}</td>
                    <td>
                      <div className="d-flex align-items-center">
                        {getStatusIcon(plugin.status)}
                        <Badge bg={getStatusVariant(plugin.status)} className="ms-2">
                          {plugin.status}
                        </Badge>
                      </div>
                    </td>
                    <td>{plugin.author}</td>
                    <td>
                      <Button
                        variant="outline-info"
                        size="sm"
                        onClick={() => fetchPluginDetails(key)}
                      >
                        <Info size={14} className="me-1" />
                        Details
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Card.Body>
      </Card>

      {/* Plugin Details Modal */}
      <Modal show={showModal} onHide={() => setShowModal(false)} size="lg" centered>
        <Modal.Header closeButton className={isDark ? 'bg-dark border-secondary text-light' : ''}>
          <Modal.Title>Plugin Details: {selectedPlugin}</Modal.Title>
        </Modal.Header>
        <Modal.Body className={isDark ? 'bg-dark text-light' : ''}>
          {pluginDetails && (
            <div>
              <div className="row mb-3">
                <div className="col-md-6">
                  <strong>Name:</strong> {pluginDetails.name}
                </div>
                <div className="col-md-6">
                  <strong>Version:</strong> <Badge bg="info">{pluginDetails.version}</Badge>
                </div>
              </div>
              <div className="row mb-3">
                <div className="col-md-6">
                  <strong>Status:</strong>
                  <div className="d-flex align-items-center mt-1">
                    {getStatusIcon(pluginDetails.status)}
                    <Badge bg={getStatusVariant(pluginDetails.status)} className="ms-2">
                      {pluginDetails.status}
                    </Badge>
                  </div>
                </div>
                <div className="col-md-6">
                  <strong>API Version:</strong> {pluginDetails.api_version}
                </div>
              </div>
              <div className="mb-3">
                <strong>Description:</strong>
                <p className="mt-2 text-muted">{pluginDetails.description}</p>
              </div>
              <div className="mb-3">
                <strong>Author:</strong> {pluginDetails.author}
              </div>
              {pluginDetails.dependencies && pluginDetails.dependencies.length > 0 && (
                <div className="mb-3">
                  <strong>Dependencies:</strong>
                  <div className="mt-2">
                    {pluginDetails.dependencies.map((dep: string, index: number) => (
                      <Badge key={index} bg="secondary" className="me-2 mb-1">
                        {dep}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
              {pluginDetails.health && (
                <div className="mb-3">
                  <strong>Health Status:</strong>
                  <pre className={`mt-2 p-2 rounded ${isDark ? 'bg-secondary' : 'bg-light'}`}>
                    {JSON.stringify(pluginDetails.health, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}
        </Modal.Body>
        <Modal.Footer className={isDark ? 'bg-dark border-secondary' : ''}>
          <Button variant="secondary" onClick={() => setShowModal(false)}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default PluginManagement;
