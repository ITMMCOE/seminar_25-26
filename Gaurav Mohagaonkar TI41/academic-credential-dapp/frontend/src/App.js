import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import IssueCredential from './components/IssueCredential';
import ViewCredentials from './components/ViewCredentials';
import VerifyCredential from './components/VerifyCredential';
import { AuthProvider, useAuth } from './context/AuthContext';

function PrivateRoute({ children }) {
  const { token } = useAuth();
  return token ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/dashboard"
              element={
                <PrivateRoute>
                  <Dashboard />
                </PrivateRoute>
              }
            />
            <Route
              path="/issue-credential"
              element={
                <PrivateRoute>
                  <IssueCredential />
                </PrivateRoute>
              }
            />
            <Route
              path="/view-credentials"
              element={
                <PrivateRoute>
                  <ViewCredentials />
                </PrivateRoute>
              }
            />
            <Route path="/verify/:credentialId" element={<VerifyCredential />} />
            <Route path="/" element={<Navigate to="/login" />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
