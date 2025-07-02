import React, { useState } from 'react';
import { Card, Form, Button, Row, Col, Table, Badge, Tabs, Tab, Alert, ProgressBar } from 'react-bootstrap';
import { useTheme } from '../../contexts/ThemeContext';
import { useNotifications } from '../../contexts/NotificationContext';
import { Globe, Search, Code, Play, Download, Eye, TestTube } from 'lucide-react';

const WebTestingApp: React.FC = () => {
  const { isDark } = useTheme();
  const { addNotification } = useNotifications();
  const [activeTab, setActiveTab] = useState('crawler');
  const [url, setUrl] = useState('');
  const [crawlDepth, setCrawlDepth] = useState(2);
  const [crawling, setCrawling] = useState(false);
  const [crawlProgress, setCrawlProgress] = useState(0);
  const [pages, setPages] = useState<any[]>([]);
  const [generating, setGenerating] = useState(false);

  const startCrawling = async () => {
    if (!url) {
      addNotification({
        type: 'warning',
        title: 'URL Required',
        message: 'Please enter a URL to crawl'
      });
      return;
    }

    setCrawling(true);
    setCrawlProgress(0);
    
    // Simulate crawling progress
    const interval = setInterval(() => {
      setCrawlProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setCrawling(false);
          setPages([
            {
              url: url,
              title: 'Homepage',
              elements: 15,
              forms: 2,
              links: 8,
              status: 'completed'
            },
            {
              url: url + '/about',
              title: 'About Page',
              elements: 12,
              forms: 1,
              links: 5,
              status: 'completed'
            },
            {
              url: url + '/contact',
              title: 'Contact Page',
              elements: 18,
              forms: 3,
              links: 6,
              status: 'completed'
            }
          ]);
          setActiveTab('pages');
          addNotification({
            type: 'success',
            title: 'Crawling Complete',
            message: `Successfully crawled ${url} and found 3 pages`
          });
          return 100;
        }
        return prev + 10;
      });
    }, 300);
  };

  const generateTests = async (pageUrl: string) => {
    setGenerating(true);
    addNotification({
      type: 'info',
      title: 'Generating Tests',
      message: `AI is generating Playwright tests for ${pageUrl}...`
    });

    // Simulate test generation
    setTimeout(() => {
      setGenerating(false);
      setActiveTab('tests');
      addNotification({
        type: 'success',
        title: 'Tests Generated',
        message: 'Playwright test scripts have been generated successfully'
      });
    }, 2000);
  };

  return (
    <div className={`p-4 ${isDark ? 'text-light' : 'text-dark'}`}>
      <div className="d-flex align-items-center mb-4">
        <Globe size={24} className="me-2" />
        <h2 className="mb-0">Web UI Testing Automation</h2>
      </div>

      <Tabs
        activeKey={activeTab}
        onSelect={(k) => k && setActiveTab(k)}
        className={`mb-4 ${isDark ? 'nav-dark' : ''}`}
      >
        <Tab eventKey="crawler" title={
          <span><Search size={16} className="me-2" />URL Crawler</span>
        }>
          <Card className={isDark ? 'bg-dark border-secondary' : ''}>
            <Card.Header className={isDark ? 'bg-dark border-secondary text-light' : ''}>
              <h5 className="mb-0">Website Crawling Configuration</h5>
            </Card.Header>
            <Card.Body className={isDark ? 'bg-dark text-light' : ''}>
              <Row>
                <Col md={8}>
                  <Form.Group className="mb-3">
                    <Form.Label>Target URL</Form.Label>
                    <Form.Control
                      type="url"
                      placeholder="https://example.com"
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                      className={isDark ? 'bg-dark text-light border-secondary' : ''}
                    />
                    <Form.Text className="text-muted">
                      Enter the base URL of the website to crawl and analyze
                    </Form.Text>
                  </Form.Group>

                  <Row>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Crawl Depth</Form.Label>
                        <Form.Select
                          value={crawlDepth}
                          onChange={(e) => setCrawlDepth(Number(e.target.value))}
                          className={isDark ? 'bg-dark text-light border-secondary' : ''}
                        >
                          <option value={1}>1 level (homepage only)</option>
                          <option value={2}>2 levels</option>
                          <option value={3}>3 levels</option>
                          <option value={4}>4 levels (deep crawl)</option>
                        </Form.Select>
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Browser Type</Form.Label>
                        <Form.Select className={isDark ? 'bg-dark text-light border-secondary' : ''}>
                          <option value="chromium">Chromium</option>
                          <option value="firefox">Firefox</option>
                          <option value="webkit">WebKit (Safari)</option>
                        </Form.Select>
                      </Form.Group>
                    </Col>
                  </Row>

                  {crawling && (
                    <div className="mb-3">
                      <div className="d-flex justify-content-between align-items-center mb-2">
                        <span>Crawling progress...</span>
                        <span>{crawlProgress}%</span>
                      </div>
                      <ProgressBar now={crawlProgress} variant="primary" />
                    </div>
                  )}

                  <Button
                    variant="primary"
                    onClick={startCrawling}
                    disabled={!url || crawling}
                    className="me-2"
                  >
                    <Search size={16} className="me-2" />
                    {crawling ? 'Crawling...' : 'Start Crawling'}
                  </Button>
                </Col>
                <Col md={4}>
                  <Card className={`h-100 ${isDark ? 'bg-secondary border-secondary' : 'bg-light'}`}>
                    <Card.Body>
                      <h6>Crawler Features</h6>
                      <ul className="list-unstyled small">
                        <li>✓ Intelligent page discovery</li>
                        <li>✓ Element extraction</li>
                        <li>✓ Form detection</li>
                        <li>✓ Link analysis</li>
                        <li>✓ Responsive design testing</li>
                        <li>✓ Performance metrics</li>
                      </ul>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Tab>

        <Tab eventKey="pages" title={
          <span><Eye size={16} className="me-2" />Discovered Pages</span>
        }>
          {pages.length > 0 ? (
            <Card className={isDark ? 'bg-dark border-secondary' : ''}>
              <Card.Header className={`d-flex justify-content-between align-items-center ${isDark ? 'bg-dark border-secondary text-light' : ''}`}>
                <h5 className="mb-0">Crawled Pages ({pages.length})</h5>
                <Button variant="outline-primary" size="sm">
                  <Download size={14} className="me-1" />
                  Export Report
                </Button>
              </Card.Header>
              <Card.Body className={isDark ? 'bg-dark text-light' : ''}>
                <Table responsive className={isDark ? 'table-dark' : ''}>
                  <thead>
                    <tr>
                      <th>URL</th>
                      <th>Page Title</th>
                      <th>Elements</th>
                      <th>Forms</th>
                      <th>Links</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {pages.map((page, index) => (
                      <tr key={index}>
                        <td className="text-break">
                          <small>{page.url}</small>
                        </td>
                        <td className="fw-bold">{page.title}</td>
                        <td>
                          <Badge bg="info">{page.elements}</Badge>
                        </td>
                        <td>
                          <Badge bg="warning">{page.forms}</Badge>
                        </td>
                        <td>
                          <Badge bg="secondary">{page.links}</Badge>
                        </td>
                        <td>
                          <Badge bg="success">{page.status}</Badge>
                        </td>
                        <td>
                          <Button
                            variant="outline-primary"
                            size="sm"
                            onClick={() => generateTests(page.url)}
                            disabled={generating}
                          >
                            <TestTube size={14} className="me-1" />
                            Generate Tests
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </Card.Body>
            </Card>
          ) : (
            <Card className={isDark ? 'bg-dark border-secondary' : ''}>
              <Card.Body className={`text-center py-5 ${isDark ? 'bg-dark text-light' : ''}`}>
                <Eye size={48} className="text-muted mb-3" />
                <h5>No Pages Discovered</h5>
                <p className="text-muted">Start crawling a website to discover pages and elements</p>
              </Card.Body>
            </Card>
          )}
        </Tab>

        <Tab eventKey="tests" title={
          <span><Code size={16} className="me-2" />Generated Tests</span>
        }>
          <Card className={isDark ? 'bg-dark border-secondary' : ''}>
            <Card.Header className={`d-flex justify-content-between align-items-center ${isDark ? 'bg-dark border-secondary text-light' : ''}`}>
              <h5 className="mb-0">Playwright Test Scripts</h5>
              <div>
                <Button variant="outline-success" size="sm" className="me-2">
                  <Play size={14} className="me-1" />
                  Run Tests
                </Button>
                <Button variant="outline-primary" size="sm">
                  <Download size={14} className="me-1" />
                  Download
                </Button>
              </div>
            </Card.Header>
            <Card.Body className={isDark ? 'bg-dark text-light' : ''}>
              <div className="mb-4">
                <h6>Test Files Generated:</h6>
                <ul className="list-unstyled">
                  <li>
                    <Badge bg="primary" className="me-2">TS</Badge>
                    homepage.spec.ts
                  </li>
                  <li>
                    <Badge bg="primary" className="me-2">TS</Badge>
                    about.spec.ts
                  </li>
                  <li>
                    <Badge bg="primary" className="me-2">TS</Badge>
                    contact.spec.ts
                  </li>
                  <li>
                    <Badge bg="secondary" className="me-2">POM</Badge>
                    page-objects/
                  </li>
                </ul>
              </div>

              <Card className={`${isDark ? 'bg-secondary border-secondary' : 'bg-light'}`}>
                <Card.Header>
                  <h6 className="mb-0">Sample Generated Test (homepage.spec.ts)</h6>
                </Card.Header>
                <Card.Body>
                  <pre className={`mb-0 ${isDark ? 'text-light' : 'text-dark'}`}>
{`import { test, expect } from '@playwright/test';

test.describe('Homepage Tests', () => {
  test('should load homepage successfully', async ({ page }) => {
    await page.goto('${url || 'https://example.com'}');
    
    await expect(page).toHaveTitle(/Homepage/);
    await expect(page.locator('h1')).toBeVisible();
  });

  test('should navigate to about page', async ({ page }) => {
    await page.goto('${url || 'https://example.com'}');
    
    await page.click('a[href="/about"]');
    await expect(page).toHaveURL(/.*about/);
  });

  test('should submit contact form', async ({ page }) => {
    await page.goto('${url || 'https://example.com'}/contact');
    
    await page.fill('[name="name"]', 'Test User');
    await page.fill('[name="email"]', 'test@example.com');
    await page.click('button[type="submit"]');
    
    await expect(page.locator('.success-message')).toBeVisible();
  });
});`}
                  </pre>
                </Card.Body>
              </Card>
            </Card.Body>
          </Card>
        </Tab>
      </Tabs>
    </div>
  );
};

export default WebTestingApp;
