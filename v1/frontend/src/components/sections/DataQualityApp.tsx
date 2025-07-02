import React, { useState } from 'react';
import { Card, Form, Button, Row, Col, Table, Badge, Tabs, Tab, Alert } from 'react-bootstrap';
import { useTheme } from '../../contexts/ThemeContext';
import { useNotifications } from '../../contexts/NotificationContext';
import { Database, FileText, Play, Download, Upload, BarChart3 } from 'lucide-react';

const DataQualityApp: React.FC = () => {
  const { isDark } = useTheme();
  const { addNotification } = useNotifications();
  const [activeTab, setActiveTab] = useState('upload');
  const [file, setFile] = useState<File | null>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      addNotification({
        type: 'success',
        title: 'File Selected',
        message: `Selected ${selectedFile.name} (${(selectedFile.size / 1024 / 1024).toFixed(2)} MB)`
      });
    }
  };

  const startAnalysis = async () => {
    if (!file) {
      addNotification({
        type: 'warning',
        title: 'No File Selected',
        message: 'Please select a file before starting analysis'
      });
      return;
    }

    setLoading(true);
    // Simulate analysis
    setTimeout(() => {
      setAnalysis({
        summary: {
          totalRows: 1250,
          totalColumns: 15,
          missingValues: 45,
          duplicateRows: 12,
          dataTypes: ['string', 'integer', 'float', 'boolean']
        },
        columns: [
          { name: 'id', type: 'integer', nullCount: 0, uniqueValues: 1250 },
          { name: 'name', type: 'string', nullCount: 5, uniqueValues: 1200 },
          { name: 'email', type: 'string', nullCount: 2, uniqueValues: 1248 },
          { name: 'age', type: 'integer', nullCount: 8, uniqueValues: 65 },
          { name: 'salary', type: 'float', nullCount: 15, uniqueValues: 890 }
        ],
        qualityScore: 85
      });
      setActiveTab('results');
      setLoading(false);
      addNotification({
        type: 'success',
        title: 'Analysis Complete',
        message: 'Data quality analysis completed successfully'
      });
    }, 3000);
  };

  const generateRules = () => {
    addNotification({
      type: 'info',
      title: 'Generating Rules',
      message: 'AI-powered data quality rules are being generated...'
    });
  };

  const generatePySparkCode = () => {
    addNotification({
      type: 'info',
      title: 'Generating Code',
      message: 'PySpark data quality validation code is being generated...'
    });
  };

  return (
    <div className={`p-4 ${isDark ? 'text-light' : 'text-dark'}`}>
      <div className="d-flex align-items-center mb-4">
        <Database size={24} className="me-2" />
        <h2 className="mb-0">Data Quality Assessment</h2>
      </div>

      <Tabs
        activeKey={activeTab}
        onSelect={(k) => k && setActiveTab(k)}
        className={`mb-4 ${isDark ? 'nav-dark' : ''}`}
      >
        <Tab eventKey="upload" title={
          <span><Upload size={16} className="me-2" />Data Upload</span>
        }>
          <Card className={isDark ? 'bg-dark border-secondary' : ''}>
            <Card.Header className={isDark ? 'bg-dark border-secondary text-light' : ''}>
              <h5 className="mb-0">Upload Dataset for Analysis</h5>
            </Card.Header>
            <Card.Body className={isDark ? 'bg-dark text-light' : ''}>
              <Row>
                <Col md={8}>
                  <Form.Group className="mb-3">
                    <Form.Label>Select Dataset File</Form.Label>
                    <Form.Control
                      type="file"
                      accept=".csv,.xlsx,.json,.parquet"
                      onChange={handleFileUpload}
                      className={isDark ? 'bg-dark text-light border-secondary' : ''}
                    />
                    <Form.Text className="text-muted">
                      Supported formats: CSV, Excel, JSON, Parquet
                    </Form.Text>
                  </Form.Group>

                  {file && (
                    <Alert variant="info">
                      <FileText size={16} className="me-2" />
                      <strong>Selected:</strong> {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                    </Alert>
                  )}

                  <Button
                    variant="primary"
                    onClick={startAnalysis}
                    disabled={!file || loading}
                    className="me-2"
                  >
                    <Play size={16} className="me-2" />
                    {loading ? 'Analyzing...' : 'Start Analysis'}
                  </Button>
                </Col>
                <Col md={4}>
                  <Card className={`h-100 ${isDark ? 'bg-secondary border-secondary' : 'bg-light'}`}>
                    <Card.Body>
                      <h6>Analysis Features</h6>
                      <ul className="list-unstyled small">
                        <li>✓ Schema validation</li>
                        <li>✓ Missing value detection</li>
                        <li>✓ Duplicate identification</li>
                        <li>✓ Data type analysis</li>
                        <li>✓ Statistical profiling</li>
                        <li>✓ AI-powered insights</li>
                      </ul>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Tab>

        <Tab eventKey="results" title={
          <span><BarChart3 size={16} className="me-2" />Analysis Results</span>
        }>
          {analysis ? (
            <div>
              <Row className="mb-4">
                <Col md={3}>
                  <Card className={isDark ? 'bg-dark border-secondary' : ''}>
                    <Card.Body className={`text-center ${isDark ? 'bg-dark text-light' : ''}`}>
                      <h3 className="text-primary">{analysis.summary.totalRows.toLocaleString()}</h3>
                      <p className="mb-0 text-muted">Total Rows</p>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={3}>
                  <Card className={isDark ? 'bg-dark border-secondary' : ''}>
                    <Card.Body className={`text-center ${isDark ? 'bg-dark text-light' : ''}`}>
                      <h3 className="text-info">{analysis.summary.totalColumns}</h3>
                      <p className="mb-0 text-muted">Columns</p>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={3}>
                  <Card className={isDark ? 'bg-dark border-secondary' : ''}>
                    <Card.Body className={`text-center ${isDark ? 'bg-dark text-light' : ''}`}>
                      <h3 className="text-warning">{analysis.summary.missingValues}</h3>
                      <p className="mb-0 text-muted">Missing Values</p>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={3}>
                  <Card className={isDark ? 'bg-dark border-secondary' : ''}>
                    <Card.Body className={`text-center ${isDark ? 'bg-dark text-light' : ''}`}>
                      <h3 className="text-success">{analysis.qualityScore}%</h3>
                      <p className="mb-0 text-muted">Quality Score</p>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>

              <Card className={isDark ? 'bg-dark border-secondary' : ''}>
                <Card.Header className={`d-flex justify-content-between align-items-center ${isDark ? 'bg-dark border-secondary text-light' : ''}`}>
                  <h5 className="mb-0">Column Analysis</h5>
                  <div>
                    <Button variant="outline-primary" size="sm" className="me-2" onClick={generateRules}>
                      Generate DQ Rules
                    </Button>
                    <Button variant="outline-success" size="sm" onClick={generatePySparkCode}>
                      <Download size={14} className="me-1" />
                      Export PySpark Code
                    </Button>
                  </div>
                </Card.Header>
                <Card.Body className={isDark ? 'bg-dark text-light' : ''}>
                  <Table responsive className={isDark ? 'table-dark' : ''}>
                    <thead>
                      <tr>
                        <th>Column Name</th>
                        <th>Data Type</th>
                        <th>Null Count</th>
                        <th>Unique Values</th>
                        <th>Quality</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analysis.columns.map((col: any, index: number) => (
                        <tr key={index}>
                          <td className="fw-bold">{col.name}</td>
                          <td>
                            <Badge bg="secondary">{col.type}</Badge>
                          </td>
                          <td className={col.nullCount > 0 ? 'text-warning' : 'text-success'}>
                            {col.nullCount}
                          </td>
                          <td>{col.uniqueValues.toLocaleString()}</td>
                          <td>
                            <Badge bg={col.nullCount === 0 ? 'success' : col.nullCount < 10 ? 'warning' : 'danger'}>
                              {col.nullCount === 0 ? 'Excellent' : col.nullCount < 10 ? 'Good' : 'Poor'}
                            </Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </Card.Body>
              </Card>
            </div>
          ) : (
            <Card className={isDark ? 'bg-dark border-secondary' : ''}>
              <Card.Body className={`text-center py-5 ${isDark ? 'bg-dark text-light' : ''}`}>
                <BarChart3 size={48} className="text-muted mb-3" />
                <h5>No Analysis Results</h5>
                <p className="text-muted">Upload and analyze a dataset to see results here</p>
              </Card.Body>
            </Card>
          )}
        </Tab>

        <Tab eventKey="rules" title={
          <span><FileText size={16} className="me-2" />DQ Rules</span>
        }>
          <Card className={isDark ? 'bg-dark border-secondary' : ''}>
            <Card.Header className={isDark ? 'bg-dark border-secondary text-light' : ''}>
              <h5 className="mb-0">Generated Data Quality Rules</h5>
            </Card.Header>
            <Card.Body className={isDark ? 'bg-dark text-light' : ''}>
              <div className="text-center py-5">
                <FileText size={48} className="text-muted mb-3" />
                <h5>AI-Powered Rule Generation</h5>
                <p className="text-muted mb-4">
                  Generate intelligent data quality rules based on your dataset analysis
                </p>
                <Button variant="primary" onClick={generateRules}>
                  Generate Rules with AI
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Tab>
      </Tabs>
    </div>
  );
};

export default DataQualityApp;
