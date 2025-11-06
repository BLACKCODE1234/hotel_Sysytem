import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Dashboard.css';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <div className="dashboard-container">
      <nav className="dashboard-nav">
        <div className="nav-content">
          <h1>🏨 Hotel Dashboard</h1>
          <div className="nav-actions">
            <span className="user-info">
              Welcome, {user?.firstname || user?.username}!
            </span>
            <Link to="/booking" className="btn-primary">
              New Booking
            </Link>
            <button onClick={handleLogout} className="btn-secondary">
              Logout
            </button>
          </div>
        </div>
      </nav>

      <div className="dashboard-content">
        <div className="dashboard-header">
          <h2>Your Dashboard</h2>
          <p>Manage your bookings and account</p>
        </div>

        <div className="dashboard-cards">
          <div className="dashboard-card">
            <div className="card-icon">📋</div>
            <h3>My Bookings</h3>
            <p>View and manage your reservations</p>
            <Link to="/booking" className="card-link">
              View Bookings →
            </Link>
          </div>

          <div className="dashboard-card">
            <div className="card-icon">➕</div>
            <h3>New Booking</h3>
            <p>Make a new reservation</p>
            <Link to="/booking" className="card-link">
              Book Now →
            </Link>
          </div>

          <div className="dashboard-card">
            <div className="card-icon">👤</div>
            <h3>Profile</h3>
            <p>Manage your account information</p>
            <div className="user-details">
              <p><strong>Name:</strong> {user?.firstname} {user?.lastname}</p>
              <p><strong>Email:</strong> {user?.email}</p>
              <p><strong>Username:</strong> {user?.username}</p>
            </div>
          </div>
        </div>

        <div className="quick-actions">
          <h3>Quick Actions</h3>
          <div className="actions-grid">
            <Link to="/booking" className="action-btn">
              <span className="action-icon">🛏️</span>
              <span>Book a Room</span>
            </Link>
            <Link to="/" className="action-btn">
              <span className="action-icon">🏠</span>
              <span>Back to Home</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

