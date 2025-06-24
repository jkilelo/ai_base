export interface HealthStatus {
  status: string;
  message: string;
  timestamp: string;
  details?: any;
}

export interface DatabaseHealthStatus extends HealthStatus {
  database_status: string;
  connection_details?: {
    driver: string;
    database: string;
    pool_size?: number;
  };
}

export interface SystemHealthStatus extends HealthStatus {
  uptime?: string;
  version?: string;
  environment?: string;
}

export interface ThemeContextType {
  isDark: boolean;
  toggleTheme: () => void;
}

export interface NotificationContextType {
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
}

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: Date;
}

export interface DashboardStats {
  totalRequests: number;
  activeConnections: number;
  uptime: string;
  lastHealthCheck: Date;
}
