import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import PrivateRoute from './components/PrivateRoute';
import Layout from './components/Layout';
import AuthPage from './pages/Login';
import GoogleCallback from './pages/GoogleCallback';
import Dashboard from './pages/Dashboard';
import AutonomousCampaign from './pages/CustomerManager';
import EmailTemplates from './pages/EmailTemplates';
import FileManager from './pages/FileManager';
import SenderManagement from './pages/SenderManagement';
import Pricing from './pages/Pricing';
import SubscriptionSummary from './pages/SubscriptionSummary';
import Settings from './pages/Settings';
import Reports from './pages/Reports';

// Component to redirect based on authentication status
function HomeRedirect() {
  const token = localStorage.getItem('token');
  return token ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />;
}

function App() {
  return (
    <AppProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<AuthPage />} />
          <Route path="/register" element={<AuthPage />} />
          <Route path="/auth/callback" element={<GoogleCallback />} />
          <Route 
            path="/dashboard" 
            element={
              <PrivateRoute>
                <Layout>
                  <Dashboard />
                </Layout>
              </PrivateRoute>
            } 
          />
          <Route 
            path="/customers" 
            element={
              <PrivateRoute>
                <Layout>
                  <AutonomousCampaign />
                </Layout>
              </PrivateRoute>
            } 
          />
          <Route 
            path="/email-templates" 
            element={
              <PrivateRoute>
                <Layout>
                  <EmailTemplates />
                </Layout>
              </PrivateRoute>
            } 
          />
          <Route 
            path="/files" 
            element={
              <PrivateRoute>
                <Layout>
                  <FileManager />
                </Layout>
              </PrivateRoute>
            } 
          />
          <Route 
            path="/sender-management" 
            element={
              <PrivateRoute>
                <Layout>
                  <SenderManagement />
                </Layout>
              </PrivateRoute>
            } 
          />
          <Route 
            path="/pricing" 
            element={
              <PrivateRoute>
                <Layout>
                  <Pricing />
                </Layout>
              </PrivateRoute>
            } 
          />
          <Route 
            path="/pricing/subscribe" 
            element={
              <PrivateRoute>
                <Layout>
                  <SubscriptionSummary />
                </Layout>
              </PrivateRoute>
            } 
          />
          <Route 
            path="/settings" 
            element={
              <PrivateRoute>
                <Layout>
                  <Settings />
                </Layout>
              </PrivateRoute>
            } 
          />
          <Route 
            path="/reports" 
            element={
              <PrivateRoute>
                <Layout>
                  <Reports />
                </Layout>
              </PrivateRoute>
            } 
          />
          <Route path="/google-login-success" element={<AuthPage />} />
          <Route path="/" element={<HomeRedirect />} />
        </Routes>
      </Router>
    </AppProvider>
  );
}

export default App;
