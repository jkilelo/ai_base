import React, { useState, useEffect } from 'react';
import { Card, Table, Badge, Button, Modal, Form, Spinner, Alert, Row, Col } from 'react-bootstrap';
import { useTheme } from '../../contexts/ThemeContext';
import { useNotifications } from '../../contexts/NotificationContext';
import axios from 'axios';
import { Bot, Plus, Settings, Brain, Database } from 'lucide-react';

interface LLMProvider {
  name: string;
  type: string;
  status: string;
  model?: string;
  apiKey?: string;
}

interface LLMProvidersResponse {
  providers: string[];
  templates: string[];
}

const LLMProviderManagement: React.FC = () => {
  const { isDark } = useTheme();
  const { addNotification } = useNotifications();
  const [providers, setProviders] = useState<string[]>([]);
  const [templates, setTemplates] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);

  const api = axios.create({
    baseURL: 'http://localhost:8001',
    timeout: 10000,
  });

  useEffect(() => {
    fetchProviders();
  }, []);

  const fetchProviders = async () => {
    try {
      setLoading(true);
      const response = await api.get<LLMProvidersResponse>('/api/v1/llm/providers');
      setProviders(response.data.providers);
      setTemplates(response.data.templates);
      setError(null);
    } catch (err) {
      setError('Failed to fetch LLM providers');
      addNotification({
        type: 'error',
        title: 'Error',
        message: 'Failed to fetch LLM providers'
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center min-vh-25">
        <Spinner animation="border" variant={isDark ? 'light' : 'primary'} />
        <span className={`ms-2 ${isDark ? 'text-light' : 'text-dark'}`}>Loading LLM providers...</span>
      </div>
    );
  }

  return (
    <div className={`p-4 ${isDark ? 'text-light' : 'text-dark'}`}>
      <div className="d-flex align-items-center justify-content-between mb-4">
        <div className="d-flex align-items-center">
          <Bot size={24} className="me-2" />
          <h2 className="mb-0">LLM Provider Management</h2>
        </div>
        <Button variant="primary" onClick={() => setShowModal(true)}>
          <Plus size={16} className="me-2" />
          Add Provider
        </Button>
      </div>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Row>
        <Col md={8}>
          <Card className={isDark ? 'bg-dark border-secondary' : ''}>
            <Card.Header className={`d-flex justify-content-between align-items-center ${isDark ? 'bg-dark border-secondary text-light' : ''}`}>
              <h5 className="mb-0">Configured Providers ({providers.length})</h5>
              <Button variant="outline-primary" size="sm" onClick={fetchProviders}>
                Refresh
              </Button>
            </Card.Header>
            <Card.Body className={isDark ? 'bg-dark text-light' : ''}>
              {providers.length === 0 ? (
                <div className="text-center py-4">
                  <Bot size={48} className="text-muted mb-3" />
                  <p className="text-muted">No LLM providers configured</p>
                  <p className="text-muted small">Add providers to enable AI-powered features</p>
                </div>
              ) : (
                <Table responsive className={isDark ? 'table-dark' : ''}>
                  <thead>
                    <tr>
                      <th>Provider</th>
                      <th>Status</th>
                      <th>Model</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {providers.map((provider, index) => (
                      <tr key={index}>
                        <td className="fw-bold">
                          <Brain size={16} className="me-2" />
                          {provider}
                        </td>
                        <td>
                          <Badge bg="success">Active</Badge>
                        </td>
                        <td className="text-muted">GPT-4</td>
                        <td>
                          <Button variant="outline-secondary" size="sm" className="me-2">
                            <Settings size={14} className="me-1" />
                            Configure
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </Card.Body>
          </Card>
        </Col>

        <Col md={4}>
          <Card className={isDark ? 'bg-dark border-secondary' : ''}>
            <Card.Header className={`${isDark ? 'bg-dark border-secondary text-light' : ''}`}>
              <h5 className="mb-0">
                <Database size={16} className="me-2" />
                Available Templates ({templates.length})
              </h5>
            </Card.Header>
            <Card.Body className={isDark ? 'bg-dark text-light' : ''}>
              {templates.length === 0 ? (
                <p className="text-muted">No templates available</p>
              ) : (
                <div>
                  {templates.map((template, index) => (
                    <div key={index} className="d-flex align-items-center justify-content-between mb-2">
                      <span className="small">{template.replace(/_/g, ' ')}</span>
                      <Badge bg="info" className="small">Ready</Badge>
                    </div>
                  ))}
                </div>
              )}
            </Card.Body>
          </Card>

          <Card className={`mt-3 ${isDark ? 'bg-dark border-secondary' : ''}`}>
            <Card.Header className={`${isDark ? 'bg-dark border-secondary text-light' : ''}`}>
              <h6 className="mb-0">Quick Setup</h6>
            </Card.Header>
            <Card.Body className={isDark ? 'bg-dark text-light' : ''}>
              <p className="small text-muted mb-3">
                Get started quickly with popular LLM providers:
              </p>
              <div className="d-grid gap-2">
                <Button variant="outline-primary" size="sm">
                  Setup OpenAI
                </Button>
                <Button variant="outline-secondary" size="sm">
                  Setup Azure OpenAI
                </Button>
                <Button variant="outline-info" size="sm">
                  Setup Anthropic
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Add Provider Modal */}
      <Modal show={showModal} onHide={() => setShowModal(false)} size="lg" centered>
        <Modal.Header closeButton className={isDark ? 'bg-dark border-secondary text-light' : ''}>
          <Modal.Title>Add New LLM Provider</Modal.Title>
        </Modal.Header>
        <Modal.Body className={isDark ? 'bg-dark text-light' : ''}>
          <Form>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Provider Type</Form.Label>
                  <Form.Select className={isDark ? 'bg-dark text-light border-secondary' : ''}>
                    <option value="">Select provider...</option>
                    <option value="openai">OpenAI</option>
                    <option value="azure-openai">Azure OpenAI</option>
                    <option value="anthropic">Anthropic</option>
                    <option value="huggingface">Hugging Face</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Provider Name</Form.Label>
                  <Form.Control 
                    type="text" 
                    placeholder="Enter provider name..."
                    className={isDark ? 'bg-dark text-light border-secondary' : ''}
                  />
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Label>API Key</Form.Label>
              <Form.Control 
                type="password" 
                placeholder="Enter API key..."
                className={isDark ? 'bg-dark text-light border-secondary' : ''}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Model</Form.Label>
              <Form.Control 
                type="text" 
                placeholder="e.g., gpt-4, claude-3-sonnet..."
                className={isDark ? 'bg-dark text-light border-secondary' : ''}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Base URL (optional)</Form.Label>
              <Form.Control 
                type="url" 
                placeholder="Custom API endpoint..."
                className={isDark ? 'bg-dark text-light border-secondary' : ''}
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer className={isDark ? 'bg-dark border-secondary' : ''}>
          <Button variant="secondary" onClick={() => setShowModal(false)}>
            Cancel
          </Button>
          <Button variant="primary">
            Add Provider
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default LLMProviderManagement;
