import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import './AdminDashboard.css';

const AdminDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [statsRes, bookingsRes] = await Promise.all([
        api.get('/admin/dashboard/stats'),
        api.get('/admin/bookings'),
      ]);
      setStats(statsRes.data);
      setBookings(bookingsRes.data);
    } catch (error) {
      setError('Failed to load dashboard data');
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (bookingId, newStatus) => {
    try {
      await api.put(`/admin/bookings/${bookingId}/status`, { status: newStatus });
      // Refresh bookings after update
      const response = await api.get('/admin/bookings');
      setBookings(response.data);
    } catch (error) {
      alert('Failed to update booking status');
      console.error('Error updating status:', error);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const getStatusBadgeClass = (status) => {
    const statusClasses = {
      pending: 'status-pending',
      confirmed: 'status-confirmed',
      cancelled: 'status-cancelled',
      completed: 'status-completed',
    };
    return statusClasses[status] || '';
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard-container">
      <nav className="admin-nav">
        <div className="nav-content">
          <h1>🔧 Admin Dashboard</h1>
          <div className="nav-actions">
            <span className="user-info">Admin: {user?.email}</span>
            <button onClick={handleLogout} className="btn-secondary">
              Logout
            </button>
          </div>
        </div>
      </nav>

      <div className="admin-content">
        {error && <div className="error-message">{error}</div>}

        {stats && (
          <div className="stats-section">
            <h2>Dashboard Statistics</h2>
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon">📊</div>
                <div className="stat-info">
                  <h3>{stats.totalBookings || 0}</h3>
                  <p>Total Bookings</p>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon">✅</div>
                <div className="stat-info">
                  <h3>{stats.confirmedBookings || 0}</h3>
                  <p>Confirmed</p>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon">⏳</div>
                <div className="stat-info">
                  <h3>{stats.pendingBookings || 0}</h3>
                  <p>Pending</p>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon">👥</div>
                <div className="stat-info">
                  <h3>{stats.activeGuests || 0}</h3>
                  <p>Active Guests</p>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon">🛏️</div>
                <div className="stat-info">
                  <h3>{stats.availableRooms || 0}</h3>
                  <p>Available Rooms</p>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon">🏨</div>
                <div className="stat-info">
                  <h3>{stats.totalRooms || 0}</h3>
                  <p>Total Rooms</p>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="bookings-section">
          <div className="section-header">
            <h2>Recent Bookings</h2>
            <button onClick={fetchDashboardData} className="btn-refresh">
              🔄 Refresh
            </button>
          </div>

          {bookings.length === 0 ? (
            <div className="no-bookings">
              <p>No bookings found</p>
            </div>
          ) : (
            <div className="bookings-table-container">
              <table className="bookings-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Guest Name</th>
                    <th>Email</th>
                    <th>Phone</th>
                    <th>Room Type</th>
                    <th>Guests</th>
                    <th>Check-in</th>
                    <th>Check-out</th>
                    <th>Duration</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {bookings.map((booking) => (
                    <tr key={booking.id}>
                      <td>{booking.id}</td>
                      <td>{booking.guest_name}</td>
                      <td>{booking.email}</td>
                      <td>{booking.phone}</td>
                      <td className="room-type">
                        {booking.room_type.charAt(0).toUpperCase() +
                          booking.room_type.slice(1)}
                      </td>
                      <td>{booking.people}</td>
                      <td>{booking.check_in}</td>
                      <td>{booking.check_out}</td>
                      <td>{booking.duration} days</td>
                      <td>
                        <span
                          className={`status-badge ${getStatusBadgeClass(
                            booking.status
                          )}`}
                        >
                          {booking.status}
                        </span>
                      </td>
                      <td>
                        <select
                          value={booking.status}
                          onChange={(e) =>
                            handleStatusUpdate(booking.id, e.target.value)
                          }
                          className="status-select"
                        >
                          <option value="pending">Pending</option>
                          <option value="confirmed">Confirmed</option>
                          <option value="cancelled">Cancelled</option>
                          <option value="completed">Completed</option>
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;

