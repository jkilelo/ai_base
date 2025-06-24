import React from 'react';
import { Card, Row, Col } from 'react-bootstrap';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { useTheme } from '../contexts/ThemeContext';

// Sample data for demonstration
const responseTimeData = [
  { time: '00:00', responseTime: 45 },
  { time: '04:00', responseTime: 52 },
  { time: '08:00', responseTime: 38 },
  { time: '12:00', responseTime: 65 },
  { time: '16:00', responseTime: 42 },
  { time: '20:00', responseTime: 55 },
];

const requestVolumeData = [
  { time: '00:00', requests: 120 },
  { time: '04:00', requests: 80 },
  { time: '08:00', requests: 340 },
  { time: '12:00', requests: 520 },
  { time: '16:00', requests: 480 },
  { time: '20:00', requests: 290 },
];

const statusDistribution = [
  { name: 'Success', value: 85, color: '#28a745' },
  { name: 'Warning', value: 10, color: '#ffc107' },
  { name: 'Error', value: 5, color: '#dc3545' },
];

interface ChartsGridProps {
  healthData: any;
}

const ChartsGrid: React.FC<ChartsGridProps> = ({ healthData }) => {
  const { isDark } = useTheme();

  const chartTheme = {
    grid: isDark ? '#374151' : '#e5e7eb',
    text: isDark ? '#f3f4f6' : '#374151',
    background: isDark ? 'transparent' : 'transparent'
  };

  return (
    <Row className="g-4">
      {/* Response Time Chart */}
      <Col lg={6}>
        <Card className={`chart-container ${isDark ? 'dark' : ''}`}>
          <Card.Header>
            <h5 className="mb-0">Response Time (ms)</h5>
          </Card.Header>
          <Card.Body>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={responseTimeData}>
                <CartesianGrid strokeDasharray="3 3" stroke={chartTheme.grid} />
                <XAxis dataKey="time" stroke={chartTheme.text} />
                <YAxis stroke={chartTheme.text} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: isDark ? '#374151' : '#ffffff',
                    border: `1px solid ${chartTheme.grid}`,
                    color: chartTheme.text
                  }}
                />
                <Line 
                  type="monotone" 
                  dataKey="responseTime" 
                  stroke="#667eea" 
                  strokeWidth={2}
                  dot={{ fill: '#667eea', strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6, fill: '#764ba2' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card.Body>
        </Card>
      </Col>

      {/* Request Volume Chart */}
      <Col lg={6}>
        <Card className={`chart-container ${isDark ? 'dark' : ''}`}>
          <Card.Header>
            <h5 className="mb-0">Request Volume</h5>
          </Card.Header>
          <Card.Body>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={requestVolumeData}>
                <CartesianGrid strokeDasharray="3 3" stroke={chartTheme.grid} />
                <XAxis dataKey="time" stroke={chartTheme.text} />
                <YAxis stroke={chartTheme.text} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: isDark ? '#374151' : '#ffffff',
                    border: `1px solid ${chartTheme.grid}`,
                    color: chartTheme.text
                  }}
                />
                <Area 
                  type="monotone" 
                  dataKey="requests" 
                  stroke="#667eea" 
                  fill="url(#colorGradient)"
                  strokeWidth={2}
                />
                <defs>
                  <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#667eea" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#667eea" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
              </AreaChart>
            </ResponsiveContainer>
          </Card.Body>
        </Card>
      </Col>

      {/* Status Distribution */}
      <Col lg={6}>
        <Card className={`chart-container ${isDark ? 'dark' : ''}`}>
          <Card.Header>
            <h5 className="mb-0">Status Distribution</h5>
          </Card.Header>
          <Card.Body>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={statusDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {statusDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: isDark ? '#374151' : '#ffffff',
                    border: `1px solid ${chartTheme.grid}`,
                    color: chartTheme.text
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </Card.Body>
        </Card>
      </Col>

      {/* Health Status Summary */}
      <Col lg={6}>
        <Card className={`chart-container ${isDark ? 'dark' : ''}`}>
          <Card.Header>
            <h5 className="mb-0">Health Status Summary</h5>
          </Card.Header>
          <Card.Body>
            <div className="d-flex flex-column gap-3">
              <div className="d-flex justify-content-between align-items-center">
                <span>API Health</span>
                <span className={`badge ${healthData?.health?.status === 'healthy' ? 'bg-success' : 'bg-danger'}`}>
                  {healthData?.health?.status || 'Unknown'}
                </span>
              </div>
              <div className="d-flex justify-content-between align-items-center">
                <span>Database Status</span>
                <span className={`badge ${healthData?.database?.database_status === 'connected' ? 'bg-success' : 'bg-danger'}`}>
                  {healthData?.database?.database_status || 'Unknown'}
                </span>
              </div>
              <div className="d-flex justify-content-between align-items-center">
                <span>System Uptime</span>
                <span className="badge bg-info">
                  {healthData?.system?.uptime || 'Unknown'}
                </span>
              </div>
              <div className="d-flex justify-content-between align-items-center">
                <span>Last Check</span>
                <span className="text-muted small">
                  {healthData?.health?.timestamp ? new Date(healthData.health.timestamp).toLocaleTimeString() : 'Never'}
                </span>
              </div>
            </div>
          </Card.Body>
        </Card>
      </Col>
    </Row>
  );
};

export default ChartsGrid;
