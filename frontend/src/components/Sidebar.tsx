import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Sidebar: React.FC = () => {
  const { user } = useAuth();

  const linkClass =
    'block py-2 px-4 rounded hover:bg-blue-100 text-sm font-medium transition';

  const activeClass =
    'bg-blue-200 text-blue-800 font-semibold';

  return (
    <aside className="w-64 bg-white border-r shadow-sm p-4 h-full">
      <nav className="space-y-1">
        <NavLink
          to="/"
          className={({ isActive }) => `${linkClass} ${isActive ? activeClass : ''}`}
        >
          Dashboard
        </NavLink>
        <NavLink
          to="/profile"
          className={({ isActive }) => `${linkClass} ${isActive ? activeClass : ''}`}
        >
          Profile
        </NavLink>
        <NavLink
          to="/predictions"
          className={({ isActive }) => `${linkClass} ${isActive ? activeClass : ''}`}
        >
          Predictions
        </NavLink>
        <NavLink
          to="/transactions"
          className={({ isActive }) => `${linkClass} ${isActive ? activeClass : ''}`}
        >
          Transactions
        </NavLink>
        <NavLink
          to="/settings"
          className={({ isActive }) => `${linkClass} ${isActive ? activeClass : ''}`}
        >
          Settings
        </NavLink>
        {user?.role === 'admin' && (
          <NavLink
            to="/admin/models"
            className={({ isActive }) => `${linkClass} ${isActive ? activeClass : ''}`}
          >
            Admin: Models
          </NavLink>
        )}
      </nav>
    </aside>
  );
};

export default Sidebar;
