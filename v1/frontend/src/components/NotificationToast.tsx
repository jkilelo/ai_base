import React from 'react';
import { Toast, ToastContainer } from 'react-bootstrap';
import { CheckCircle, AlertTriangle, XCircle, Info } from 'lucide-react';
import { useNotifications } from '../contexts/NotificationContext';

const NotificationToast: React.FC = () => {
  const { notifications, removeNotification } = useNotifications();

  const getIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle size={20} className="text-success" />;
      case 'warning':
        return <AlertTriangle size={20} className="text-warning" />;
      case 'error':
        return <XCircle size={20} className="text-danger" />;
      default:
        return <Info size={20} className="text-info" />;
    }
  };

  const getVariant = (type: string) => {
    switch (type) {
      case 'success':
        return 'success';
      case 'warning':
        return 'warning';
      case 'error':
        return 'danger';
      default:
        return 'info';
    }
  };

  return (
    <ToastContainer position="top-end" className="p-3 toast-container">
      {notifications.slice(0, 3).map((notification) => (
        <Toast
          key={notification.id}
          onClose={() => removeNotification(notification.id)}
          show={true}
          delay={5000}
          autohide
          bg={getVariant(notification.type)}
        >
          <Toast.Header>
            <div className="me-2">
              {getIcon(notification.type)}
            </div>
            <strong className="me-auto">{notification.title}</strong>
            <small>{notification.timestamp.toLocaleTimeString()}</small>
          </Toast.Header>
          <Toast.Body className="text-white">
            {notification.message}
          </Toast.Body>
        </Toast>
      ))}
    </ToastContainer>
  );
};

export default NotificationToast;
