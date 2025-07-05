import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import PrivateRoute from './components/PrivateRoute';
import Layout from './components/Layout';
import AuthPage from './pages/Login';
import Dashboard from './pages/Dashboard';
import AutonomousCampaign from './pages/CustomerManager';
import EmailTemplates from './pages/EmailTemplates';
import FileManager from './pages/FileManager';
import SenderManagement from './pages/SenderManagement';
import Pricing from './pages/Pricing';
import SubscriptionSummary from './pages/SubscriptionSummary';
import Settings from './pages/Settings';
import Reports from './pages/Reports';

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
        <Route path="/" element={<AuthPage />} />
      </Routes>
    </Router>
  );
}

export default App;
