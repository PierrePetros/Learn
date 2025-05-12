import React, { useState, useEffect, useCallback } from 'react';
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import Profile from './components/Profile';
import Math from './components/Math';
import Informatics from './components/Informatics';
import MathTheory from './components/MathTheory';
import MathPractice from './components/MathPractice';
import MathSandbox from './components/MathSandbox';
import InformaticsTheory from './components/InformaticsTheory';
import InformaticsPractice from './components/InformaticsPractice';
import InformaticsSandbox from './components/InformaticsSandbox';
import Login from './components/Login';
import Register from './components/Register';
import './index.css';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      setIsLoggedIn(true);
      //navigate('/profile'); // Remove initial navigation
    }
  }, [navigate]);

  const handleLogin = useCallback((token) => {
    localStorage.setItem('access_token', token);
    setIsLoggedIn(true);
    navigate('/profile');
  }, [navigate]);

  const handleLogout = useCallback(() => {
    localStorage.removeItem('access_token');
    setIsLoggedIn(false);
    navigate('/login');
  }, [navigate]);

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Учись</h1>
      </header>
      <main className="app-main">
        <Routes>
          <Route path="/login" element={<Login onLogin={handleLogin} />} />
          <Route path="/register" element={<Register />} />
          <Route path="/" element={isLoggedIn ? <Navigate to="/profile" /> : <Navigate to="/login" />} />
          <Route path="/profile" element={<Profile onLogout={handleLogout} />} />
          <Route path="/math" element={isLoggedIn ? <Math /> : <Navigate to="/login" />} />
          <Route path="/informatics" element={isLoggedIn ? <Informatics /> : <Navigate to="/login" />} />
          <Route path="/math_theory" element={isLoggedIn ? <MathTheory /> : <Navigate to="/login" />} />
          <Route path="/math_practice" element={isLoggedIn ? <MathPractice /> : <Navigate to="/login" />} />
          <Route path="/math_sandbox" element={isLoggedIn ? <MathSandbox /> : <Navigate to="/login" />} />
          <Route path="/informatics_theory" element={isLoggedIn ? <InformaticsTheory /> : <Navigate to="/login" />} />
          <Route path="/informatics_practice" element={isLoggedIn ? <InformaticsPractice /> : <Navigate to="/login" />} />
          <Route path="/informatics_sandbox" element={isLoggedIn ? <InformaticsSandbox /> : <Navigate to="/login" />} />
        </Routes>
      </main>
      <footer className="app-footer">
      </footer>
    </div>
  );
}

export default App;
