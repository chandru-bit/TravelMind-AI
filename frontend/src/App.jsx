import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';

import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { OnboardingPage } from './pages/OnboardingPage';
import { DashboardPage } from './pages/DashboardPage';
import { PlanTripPage } from './pages/PlanTripPage';
import { RecommendationsPage } from './pages/RecommendationsPage';
import { PricePredictionPage } from './pages/PricePredictionPage';
import { SavedTripsPage } from './pages/SavedTripsPage';
import { ProfilePage } from './pages/ProfilePage';
import { NotFoundPage } from './pages/NotFoundPage';

const ProtectedRoute = ({ children }) => {
  const { token } = useAuth();
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

export function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen flex flex-col bg-[#0b0f19] text-gray-100">
        <Navbar />
        
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            
            <Route path="/onboarding" element={<ProtectedRoute><OnboardingPage /></ProtectedRoute>} />
            <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
            <Route path="/plan" element={<ProtectedRoute><PlanTripPage /></ProtectedRoute>} />
            <Route path="/recommendations" element={<RecommendationsPage />} />
            <Route path="/predictions" element={<ProtectedRoute><PricePredictionPage /></ProtectedRoute>} />
            <Route path="/saved-trips" element={<ProtectedRoute><SavedTripsPage /></ProtectedRoute>} />
            <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />

            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </main>

        <Footer />
      </div>
    </AuthProvider>
  );
}

export default App;
