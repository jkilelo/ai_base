import React from 'react';
import { Nav } from 'react-bootstrap';
import { 
  Home, 
  Activity, 
  Database, 
  Server, 
  BarChart3, 
  Settings,
  HelpCircle
} from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

interface SidebarProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activeSection, onSectionChange }) => {
  const { isDark } = useTheme();

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home },
    { id: 'health', label: 'Health Status', icon: Activity },
    { id: 'database', label: 'Database', icon: Database },
    { id: 'system', label: 'System Info', icon: Server },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'settings', label: 'Settings', icon: Settings },
    { id: 'help', label: 'Help', icon: HelpCircle },
  ];
  return (
    <div 
      className={`sidebar ${isDark ? 'dark' : ''} d-flex flex-column sidebar-container`}
    >
      <div className="p-3">
        <h6 className={`text-uppercase fw-bold mb-3 ${isDark ? 'text-light' : 'text-muted'}`}>
          Navigation
        </h6>
        <Nav className="flex-column">
          {menuItems.map((item) => {
            const IconComponent = item.icon;
            return (
              <Nav.Link
                key={item.id}
                onClick={() => onSectionChange(item.id)}                className={`d-flex align-items-center py-3 px-3 mb-1 rounded nav-item ${
                  activeSection === item.id ? 'active' : ''
                } ${isDark ? 'text-light' : 'text-dark'}`}
              >
                <IconComponent size={18} className="me-3" />
                <span>{item.label}</span>
              </Nav.Link>
            );
          })}
        </Nav>
      </div>
      
      {/* Bottom section */}
      <div className="mt-auto p-3 border-top">
        <div className={`small ${isDark ? 'text-light' : 'text-muted'}`}>
          <div className="mb-1">Version 1.0.0</div>
          <div>FastAPI Dashboard</div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
