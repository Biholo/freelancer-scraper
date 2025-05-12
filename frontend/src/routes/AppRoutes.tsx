import { Routes, Route, Navigate, Outlet } from 'react-router-dom';
import PublicRoutes from '@/routes/PublicRoutes';
import Error from '@/features/Error';
import Sidebar from '@/components/layout/Sidebar';
import { useAuthStore } from '@/stores/authStore';
import Loader from '@/components/ui/Loader';
import { useAutoLogin } from '@/api/queries/authQueries';
import { useEffect } from 'react';
import Dashboard from '@/features/jobs/Dashboard';
import FreelancerList from '@/features/jobs/FreelancerList';
import FreelancerDetail from '@/features/jobs/FreelancerDetail';

// Layout component that includes sidebar and outlet for child routes
const MainLayout = () => {
  return (
    <div className="min-h-screen flex flex-col md:flex-row">
      <Sidebar />
      <main className="flex-grow p-4">
        <Outlet />
      </main>
    </div>
  );
};

const AppRoutes = () => {
  const { refetch: autoLogin, isPending } = useAutoLogin();

  useEffect(() => {
    autoLogin();
  }, [autoLogin]);

  if (isPending) return <Loader />

  return (
        <Routes>
          {/* Routes publiques */}
          <Route element={<PublicRoutes />}>
        {/* Add public routes here if needed */}
          </Route>

      {/* Main layout with sidebar for all app routes */}
      <Route element={<MainLayout />}>
        {/* Job routes - these are public for demo purposes */}
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/freelancers" element={<FreelancerList />} />
        <Route path="/freelancers/:id" element={<FreelancerDetail />} />

          {/* Route par défaut */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
          <Route path="/error" element={<Error />} />
      </Route>
        </Routes>
  );
};

export default AppRoutes;
