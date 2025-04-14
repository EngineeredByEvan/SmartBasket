import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="bg-white border-b shadow-sm px-6 py-4 flex justify-between items-center">
      <h1
        className="text-xl font-bold text-blue-600 cursor-pointer"
        onClick={() => navigate('/')}
      >
        SmartBasket
      </h1>

      <div className="flex items-center gap-4">
        {user ? (
          <>
            <span className="text-sm text-gray-700">
              Logged in as <strong>{user.username}</strong>
            </span>
            <button
              onClick={handleLogout}
              className="text-sm bg-red-500 text-white px-3 py-1 rounded-md hover:bg-red-600 transition"
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <Link
              to="/login"
              className="text-sm text-blue-600 hover:underline"
            >
              Login
            </Link>
            <Link
              to="/register"
              className="text-sm text-blue-600 hover:underline"
            >
              Register
            </Link>
          </>
        )}
      </div>
    </header>
  );
};

export default Navbar;
