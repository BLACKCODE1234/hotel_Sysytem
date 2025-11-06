import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Home.css';

const Home = () => {
  const navigate = useNavigate();
  const [bookingForm, setBookingForm] = useState({
    check_in: '',
    duration: '',
    people: '',
    room_type: ''
  });

  const roomTypes = [
    {
      id: 1,
      name: 'Standard Room',
      description: 'Comfortable and affordable accommodation perfect for short stays',
      features: ['Queen Bed', 'City View', 'Free WiFi'],
      price: 'From $99/night'
    },
    {
      id: 2,
      name: 'Deluxe Room',
      description: 'Spacious rooms with premium amenities and stunning views',
      features: ['King Bed', 'Balcony', 'Mini Bar'],
      price: 'From $149/night'
    },
    {
      id: 3,
      name: 'Suite',
      description: 'Luxurious suites with separate living areas for ultimate comfort',
      features: ['King Bed', 'Living Room', 'Premium View'],
      price: 'From $249/night'
    },
    {
      id: 4,
      name: 'Executive Suite',
      description: 'The ultimate in luxury with premium amenities and exceptional service',
      features: ['King Bed', 'Dining Area', 'Panoramic View'],
      price: 'From $349/night'
    }
  ];

  const amenities = [
    { icon: '🏊', title: 'Swimming Pool', description: 'Outdoor pool with stunning views' },
    { icon: '🍽️', title: 'Fine Dining', description: 'World-class restaurant on-site' },
    { icon: '💼', title: 'Business Center', description: 'Fully equipped meeting rooms' },
    { icon: '🚗', title: 'Free Parking', description: 'Complimentary valet parking' },
    { icon: '🏋️', title: 'Fitness Center', description: '24/7 gym with modern equipment' },
    { icon: '🛎️', title: 'Concierge', description: '24-hour concierge service' }
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setBookingForm(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleBookingSearch = (e) => {
    e.preventDefault();
    // Redirect to booking page or show booking form
    navigate('/booking');
  };

  useEffect(() => {
    // Add scroll animation observer
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
          }
        });
      },
      { threshold: 0.1 }
    );

    const elements = document.querySelectorAll('.animate-on-scroll');
    elements.forEach((el) => observer.observe(el));

    return () => {
      elements.forEach((el) => observer.unobserve(el));
    };
  }, []);

  return (
    <div className="landing-page">
      {/* Navigation */}
      <nav className="navbar">
        <div className="container">
          <div className="nav-brand">
            <h1>🏨 Luxury Hotel</h1>
          </div>
          <div className="nav-links">
            <a href="#rooms">Rooms</a>
            <a href="#amenities">Amenities</a>
            <a href="#about">About</a>
            <Link to="/login" className="btn-secondary">Login</Link>
            <Link to="/signup" className="btn-primary">Sign Up</Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero">
        <div className="animated-bg">
          <div className="floating-shape shape-1"></div>
          <div className="floating-shape shape-2"></div>
          <div className="floating-shape shape-3"></div>
          <div className="floating-shape shape-4"></div>
        </div>
        <div className="hero-overlay"></div>
        <div className="hero-content">
          <h1 className="hero-title">
            <span className="gradient-text">Welcome to Luxury Hotel</span>
          </h1>
          <p className="hero-subtitle">Experience unparalleled comfort and exceptional service</p>
          <div className="hero-buttons">
            <Link to="/signup" className="btn-primary btn-large pulse-animation">Book Your Stay</Link>
            <a href="#rooms" className="btn-secondary btn-large">Explore Rooms</a>
          </div>
        </div>
      </section>

      {/* Booking Search Bar */}
      <section className="booking-search">
        <div className="container">
          <form onSubmit={handleBookingSearch} className="booking-form">
            <div className="form-group">
              <label>Check In</label>
              <input
                type="date"
                name="check_in"
                value={bookingForm.check_in}
                onChange={handleInputChange}
                required
              />
            </div>
            <div className="form-group">
              <label>Duration (Days)</label>
              <input
                type="number"
                name="duration"
                value={bookingForm.duration}
                onChange={handleInputChange}
                placeholder="Nights"
                min="1"
                required
              />
            </div>
            <div className="form-group">
              <label>Guests</label>
              <select
                name="people"
                value={bookingForm.people}
                onChange={handleInputChange}
                required
              >
                <option value="">Select</option>
                <option value="1">1 Guest</option>
                <option value="2">2 Guests</option>
                <option value="3">3 Guests</option>
                <option value="4">4 Guests</option>
                <option value="5">5+ Guests</option>
              </select>
            </div>
            <div className="form-group">
              <label>Room Type</label>
              <select
                name="room_type"
                value={bookingForm.room_type}
                onChange={handleInputChange}
                required
              >
                <option value="">Select Room</option>
                <option value="standard">Standard Room</option>
                <option value="deluxe">Deluxe Room</option>
                <option value="suite">Suite</option>
                <option value="executive">Executive Suite</option>
              </select>
            </div>
            <button type="submit" className="btn-primary btn-large">Check Availability</button>
          </form>
        </div>
      </section>

      {/* Rooms Section */}
      <section id="rooms" className="rooms-section">
        <div className="container">
          <div className="section-header">
            <h2>Our Rooms</h2>
            <p>Choose from our selection of beautifully designed rooms and suites</p>
          </div>
          <div className="rooms-grid">
            {roomTypes.map((room, index) => (
              <div key={room.id} className={`room-card animate-on-scroll room-card-${index + 1}`}>
                <div className="room-image">
                  <div className="room-placeholder">{room.name.charAt(0)}</div>
                  <div className="room-gradient-overlay"></div>
                </div>
                <div className="room-content">
                  <h3>{room.name}</h3>
                  <p className="room-description">{room.description}</p>
                  <ul className="room-features">
                    {room.features.map((feature, idx) => (
                      <li key={idx}>✓ {feature}</li>
                    ))}
                  </ul>
                  <div className="room-footer">
                    <span className="room-price">{room.price}</span>
                    <Link to="/signup" className="btn-primary btn-small">Book Now</Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Amenities Section */}
      <section id="amenities" className="amenities-section">
        <div className="container">
          <div className="section-header">
            <h2>Hotel Amenities</h2>
            <p>Everything you need for a perfect stay</p>
          </div>
          <div className="amenities-grid">
            {amenities.map((amenity, idx) => (
              <div key={idx} className={`amenity-card animate-on-scroll amenity-${idx + 1}`}>
                <div className="amenity-icon">{amenity.icon}</div>
                <h3>{amenity.title}</h3>
                <p>{amenity.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="about-section">
        <div className="container">
          <div className="about-content">
            <div className="about-text">
              <h2>About Our Hotel</h2>
              <p>
                Luxury Hotel is a premier destination for travelers seeking comfort, elegance, and 
                exceptional service. Located in the heart of the city, we offer world-class 
                accommodations with modern amenities and personalized attention to every detail.
              </p>
              <p>
                Our commitment to excellence ensures that every guest enjoys a memorable stay, 
                whether traveling for business or leisure. Experience the perfect blend of 
                sophistication and comfort at Luxury Hotel.
              </p>
              <div className="about-stats">
                <div className="stat-item animate-on-scroll">
                  <h3 className="counter-animation">500+</h3>
                  <p>Happy Guests</p>
                </div>
                <div className="stat-item animate-on-scroll">
                  <h3 className="counter-animation">50+</h3>
                  <p>Rooms</p>
                </div>
                <div className="stat-item animate-on-scroll">
                  <h3 className="counter-animation">10+</h3>
                  <p>Years Experience</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="container">
          <div className="cta-content">
            <h2>Ready to Book Your Stay?</h2>
            <p>Join thousands of satisfied guests and experience luxury like never before</p>
            <div className="cta-buttons">
              <Link to="/signup" className="btn-primary btn-large">Create Account</Link>
              <Link to="/login" className="btn-secondary btn-large">Login</Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-section">
              <h3>🏨 Luxury Hotel</h3>
              <p>Your perfect stay awaits</p>
            </div>
            <div className="footer-section">
              <h4>Quick Links</h4>
              <ul>
                <li><a href="#rooms">Rooms</a></li>
                <li><a href="#amenities">Amenities</a></li>
                <li><a href="#about">About</a></li>
              </ul>
            </div>
            <div className="footer-section">
              <h4>Account</h4>
              <ul>
                <li><Link to="/login">Login</Link></li>
                <li><Link to="/signup">Sign Up</Link></li>
              </ul>
            </div>
            <div className="footer-section">
              <h4>Contact</h4>
              <ul>
                <li>Email: info@luxuryhotel.com</li>
                <li>Phone: +1 (555) 123-4567</li>
                <li>Address: 123 Luxury Street, City</li>
              </ul>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2024 Luxury Hotel. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Home;

