import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import PrivateRoute from './components/PrivateRoute';
import AuthPage from './pages/Login';
import Dashboard from './pages/Dashboard';
import CustomerManager from './pages/CustomerManager';
import EmailTemplates from './pages/EmailTemplates';
import FileManager from './pages/FileManager';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<AuthPage />} />
        <Route path="/register" element={<AuthPage />} />
        <Route 
          path="/dashboard" 
          element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          } 
        />
        <Route 
          path="/customers" 
          element={
            <PrivateRoute>
              <CustomerManager />
            </PrivateRoute>
          } 
        />
        <Route 
          path="/email-templates" 
          element={
            <PrivateRoute>
              <EmailTemplates />
            </PrivateRoute>
          } 
        />
        <Route 
          path="/files" 
          element={
            <PrivateRoute>
              <FileManager />
            </PrivateRoute>
          } 
        />
        <Route path="/" element={<AuthPage />} />
      </Routes>
    </Router>
  );
}

export default App;
