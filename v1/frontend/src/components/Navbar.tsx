import React from 'react';
import { Navbar, Nav, Badge, Dropdown } from 'react-bootstrap';
import { Bell, Moon, Sun, Settings, User } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { useNotifications } from '../contexts/NotificationContext';

const AppNavbar: React.FC = () => {
  const { isDark, toggleTheme } = useTheme();
  const { notifications } = useNotifications();

  const unreadCount = notifications.length;

  return (
    <Navbar 
      bg={isDark ? 'dark' : 'light'} 
      variant={isDark ? 'dark' : 'light'} 
      expand="lg" 
      className="px-3 shadow-sm"
      style={{ zIndex: 1000 }}
    >
      <Navbar.Brand href="#" className="fw-bold">
        <span className="text-primary">FastAPI</span> Dashboard
      </Navbar.Brand>
      
      <Navbar.Toggle aria-controls="basic-navbar-nav" />
      
      <Navbar.Collapse id="basic-navbar-nav" className="justify-content-end">
        <Nav className="align-items-center">
          {/* Theme Toggle */}
          <Nav.Link 
            onClick={toggleTheme}
            className="d-flex align-items-center me-3"
            title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {isDark ? <Sun size={20} /> : <Moon size={20} />}
          </Nav.Link>

          {/* Notifications */}
          <Dropdown align="end" className="me-3">
            <Dropdown.Toggle 
              variant="link" 
              className="nav-link border-0 bg-transparent position-relative"
              id="notifications-dropdown"
            >
              <Bell size={20} />
              {unreadCount > 0 && (
                <Badge 
                  bg="danger" 
                  pill 
                  className="position-absolute top-0 start-100 translate-middle"
                  style={{ fontSize: '0.7rem' }}
                >
                  {unreadCount > 99 ? '99+' : unreadCount}
                </Badge>
              )}
            </Dropdown.Toggle>

            <Dropdown.Menu style={{ minWidth: '300px', maxHeight: '400px', overflowY: 'auto' }}>
              <Dropdown.Header>Notifications ({unreadCount})</Dropdown.Header>
              {notifications.length === 0 ? (
                <Dropdown.ItemText className="text-muted text-center py-3">
                  No new notifications
                </Dropdown.ItemText>
              ) : (
                notifications.slice(0, 5).map((notification) => (
                  <Dropdown.Item key={notification.id} className="border-bottom">
                    <div className="d-flex justify-content-between align-items-start">
                      <div>
                        <div className="fw-semibold">{notification.title}</div>
                        <div className="text-muted small">{notification.message}</div>                        <div className="text-muted small-timestamp">
                          {notification.timestamp.toLocaleTimeString()}
                        </div>
                      </div>
                      <Badge 
                        bg={
                          notification.type === 'error' ? 'danger' :
                          notification.type === 'warning' ? 'warning' :
                          notification.type === 'success' ? 'success' : 'info'
                        }
                      >
                        {notification.type}
                      </Badge>
                    </div>
                  </Dropdown.Item>
                ))
              )}
              {notifications.length > 5 && (
                <Dropdown.Item className="text-center text-primary">
                  View all notifications
                </Dropdown.Item>
              )}
            </Dropdown.Menu>
          </Dropdown>

          {/* Settings */}
          <Dropdown align="end" className="me-3">
            <Dropdown.Toggle 
              variant="link" 
              className="nav-link border-0 bg-transparent"
              id="settings-dropdown"
            >
              <Settings size={20} />
            </Dropdown.Toggle>

            <Dropdown.Menu>
              <Dropdown.Item href="#settings">
                <Settings size={16} className="me-2" />
                Settings
              </Dropdown.Item>
              <Dropdown.Divider />
              <Dropdown.Item href="#help">
                Help & Support
              </Dropdown.Item>
            </Dropdown.Menu>
          </Dropdown>

          {/* User Menu */}
          <Dropdown align="end">
            <Dropdown.Toggle 
              variant="link" 
              className="nav-link border-0 bg-transparent d-flex align-items-center"
              id="user-dropdown"
            >
              <User size={20} className="me-2" />
              <span className="d-none d-md-inline">Admin</span>
            </Dropdown.Toggle>

            <Dropdown.Menu>
              <Dropdown.Item href="#profile">
                <User size={16} className="me-2" />
                Profile
              </Dropdown.Item>
              <Dropdown.Divider />
              <Dropdown.Item href="#logout">
                Logout
              </Dropdown.Item>
            </Dropdown.Menu>
          </Dropdown>
        </Nav>
      </Navbar.Collapse>
    </Navbar>
  );
};

export default AppNavbar;
