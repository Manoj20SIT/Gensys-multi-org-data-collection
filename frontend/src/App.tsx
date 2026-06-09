import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home'; // your home page component
// import BasicPage from './pages/BasicPage'; // your basic page component
import Callback from './pages/Callback'; // your callback page
import ProtectedRoute from './components/ProtectedRoute';
import OrgView from './pages/OrgView';
import EditOrg from './pages/EditOrg';
import AddOrg from './pages/AddOrg';
import RunResults from './pages/RunResults';

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        {/* OAuth callback must stay public */}
        <Route path="/callback" element={<Callback />} />
       {/* Protected Home on root path */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Home />
            </ProtectedRoute>
          }
        />

        {/* Optional: keep /home too */}
        <Route
          path="/home"
          element={
            <ProtectedRoute>
              <Home />
            </ProtectedRoute>
          }
        />
        <Route
  path="/orgs/add"
  element={
    <ProtectedRoute>
      <AddOrg />
    </ProtectedRoute>
  }
/>
        <Route path="/orgs/:orgName" element={<ProtectedRoute><OrgView /></ProtectedRoute>} />
        <Route path="/orgs/:orgName/edit" element={<ProtectedRoute><EditOrg  /></ProtectedRoute>} />
        <Route path="/run-results" element={<ProtectedRoute>< RunResults/></ProtectedRoute>} />
        
       
      </Routes>
    </Router>
  );
};

export default App;
