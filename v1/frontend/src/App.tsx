import React, { useState } from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import { ThemeProvider } from './contexts/ThemeContext';
import { NotificationProvider } from './contexts/NotificationContext';
import { useTheme } from './contexts/ThemeContext';
import AppNavbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import NotificationToast from './components/NotificationToast';
import DashboardOverview from './components/sections/DashboardOverview';
import HealthStatus from './components/sections/HealthStatus';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

const AppContent: React.FC = () => {
  const { isDark } = useTheme();
  const [activeSection, setActiveSection] = useState('dashboard');

  const renderContent = () => {
    switch (activeSection) {
      case 'dashboard':
        return <DashboardOverview />;
      case 'health':
        return <HealthStatus />;
      case 'database':
        return (
          <div className={isDark ? 'text-light' : 'text-dark'}>
            <h2>Database Management</h2>
            <p>Database management features coming soon...</p>
          </div>
        );
      case 'system':
        return (
          <div className={isDark ? 'text-light' : 'text-dark'}>
            <h2>System Information</h2>
            <p>System information features coming soon...</p>
          </div>
        );
      case 'analytics':
        return (
          <div className={isDark ? 'text-light' : 'text-dark'}>
            <h2>Analytics</h2>
            <p>Analytics features coming soon...</p>
          </div>
        );
      case 'settings':
        return (
          <div className={isDark ? 'text-light' : 'text-dark'}>
            <h2>Settings</h2>
            <p>Settings features coming soon...</p>
          </div>
        );
      case 'help':
        return (
          <div className={isDark ? 'text-light' : 'text-dark'}>
            <h2>Help & Support</h2>
            <p>Help and support features coming soon...</p>
          </div>
        );
      default:
        return <DashboardOverview />;
    }
  };

  return (
    <div className={`dashboard-main ${isDark ? 'dark' : ''}`}>
      <AppNavbar />
      <Container fluid className="p-0">
        <Row className="g-0">
          <Col xs="auto">
            <Sidebar 
              activeSection={activeSection} 
              onSectionChange={setActiveSection} 
            />
          </Col>
          <Col>
            <div className={`content-area ${isDark ? 'dark' : ''}`}>
              {renderContent()}
            </div>
          </Col>
        </Row>
      </Container>
      <NotificationToast />
    </div>
  );
};

function App() {
  return (
    <ThemeProvider>
      <NotificationProvider>
        <AppContent />
      </NotificationProvider>
    </ThemeProvider>
  );
}

export default App;
