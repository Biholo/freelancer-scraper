import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import Dashboard from '@/features/jobs/Dashboard';
import FreelancerList from '@/features/jobs/FreelancerList';
import FreelancerDetail from '@/features/jobs/FreelancerDetail';

const JobRoutes = () => {
  const { isAuthenticated } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
};

// These components will be used in the AppRoutes.tsx file
export const jobRoutes = [
  {
    element: <JobRoutes />,
    children: [
      { path: "/dashboard", element: <Dashboard /> },
      { path: "/freelancers", element: <FreelancerList /> },
      { path: "/freelancers/:id", element: <FreelancerDetail /> },
    ],
  },
];

export default JobRoutes; 