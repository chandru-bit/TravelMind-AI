import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Compass, Sparkles, TrendingUp, Calendar, User, LogOut, Menu, X, Bell } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isActive = (path) => location.pathname === path;

  const navLinks = [
    { name: 'Dashboard', path: '/dashboard', icon: Sparkles },
    { name: 'Plan Trip', path: '/plan', icon: Calendar },
    { name: 'Recommendations', path: '/recommendations', icon: Compass },
    { name: 'Price Predictor', path: '/predictions', icon: TrendingUp },
    { name: 'Saved Trips', path: '/saved-trips', icon: Calendar },
  ];

  return (
    <nav className="sticky top-0 z-50 glass-panel border-b border-gray-800 bg-[#0b0f19]/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/25 group-hover:scale-105 transition-transform">
              <Compass className="w-6 h-6 text-white" />
            </div>
            <div>
              <span className="font-extrabold text-xl tracking-tight text-white">
                TravelMind <span className="gradient-text">AI</span>
              </span>
              <span className="block text-[10px] text-cyan-400 font-medium tracking-wider uppercase">
                Predict. Personalize. Plan.
              </span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-1">
            {user && navLinks.map((link) => {
              const Icon = link.icon;
              const active = isActive(link.path);
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all ${
                    active
                      ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                      : 'text-gray-300 hover:text-white hover:bg-gray-800/60'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${active ? 'text-cyan-400' : 'text-gray-400'}`} />
                  {link.name}
                </Link>
              );
            })}
          </div>

          {/* Right Action Menu */}
          <div className="hidden md:flex items-center gap-3">
            {user ? (
              <div className="flex items-center gap-3">
                <Link
                  to="/profile"
                  className="flex items-center gap-2.5 px-3 py-1.5 rounded-lg bg-gray-800/80 border border-gray-700 hover:border-cyan-500/40 transition-colors"
                >
                  <div className="w-7 h-7 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center font-bold text-xs">
                    {user.name ? user.name[0].toUpperCase() : 'U'}
                  </div>
                  <span className="text-sm font-medium text-gray-200">{user.name}</span>
                </Link>
                <button
                  onClick={() => {
                    logout();
                    navigate('/');
                  }}
                  className="p-2 text-gray-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
                  title="Logout"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  to="/login"
                  className="px-4 py-2 text-sm font-medium text-gray-300 hover:text-white transition-colors"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 rounded-lg shadow-lg shadow-cyan-500/20 transition-all transform hover:-translate-y-0.5"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="flex md:hidden">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden glass-panel border-b border-gray-800 px-4 pt-2 pb-6 space-y-2">
          {user ? (
            <>
              <div className="pb-3 mb-2 border-b border-gray-800 flex items-center gap-3">
                <div className="w-9 h-9 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center font-bold">
                  {user.name ? user.name[0].toUpperCase() : 'U'}
                </div>
                <div>
                  <div className="text-sm font-semibold text-white">{user.name}</div>
                  <div className="text-xs text-gray-400">{user.email}</div>
                </div>
              </div>
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className="block px-3 py-2 rounded-lg text-base font-medium text-gray-300 hover:bg-gray-800 hover:text-white"
                >
                  {link.name}
                </Link>
              ))}
              <button
                onClick={() => {
                  logout();
                  setMobileMenuOpen(false);
                  navigate('/');
                }}
                className="w-full text-left px-3 py-2 rounded-lg text-base font-medium text-rose-400 hover:bg-rose-500/10"
              >
                Logout
              </button>
            </>
          ) : (
            <div className="space-y-2 pt-2">
              <Link
                to="/login"
                onClick={() => setMobileMenuOpen(false)}
                className="block text-center px-4 py-2 text-gray-300 hover:text-white"
              >
                Login
              </Link>
              <Link
                to="/register"
                onClick={() => setMobileMenuOpen(false)}
                className="block text-center px-4 py-2 bg-gradient-to-r from-cyan-500 to-indigo-600 text-white rounded-lg font-medium"
              >
                Get Started
              </Link>
            </div>
          )}
        </div>
      )}
    </nav>
  );
};
