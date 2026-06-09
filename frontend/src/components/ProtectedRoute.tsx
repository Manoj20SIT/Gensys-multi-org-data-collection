import { useEffect, useRef, useState } from "react";
import authService from "../services/authService";

// Type for component props: this wrapper receives page/component as children
type ProtectedRouteProps = {
  children: React.ReactNode;
};

const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  // "checking" is true while we verify if user is logged in
  // During this time we show a loader text
  const [checking, setChecking] = useState(true);

  // Prevent multiple redirects (important in React StrictMode/dev,
  // where useEffect may run more than once)
  const redirectingRef = useRef(false);

  useEffect(() => {
    const checkAuth = async () => {
      // Check if token exists and is not expired
      const ok = authService.isAuthenticated();

      // If user is NOT authenticated
      if (!ok) {
        // Redirect only once to avoid login-loop / repeated API calls
        if (!redirectingRef.current) {
          redirectingRef.current = true;
          console.log("🔒 Not authenticated, redirecting...");
          await authService.redirectToLogin(); // sends user to OAuth login page
        }
        return; // stop here, do not render protected children
      }

      // If authenticated, allow protected page rendering
      console.log("🔓 Authenticated");
      setChecking(false);
    };

    checkAuth();
  }, []);

  // While checking auth state, show loading text
  if (checking) return <div>Checking authentication...</div>;

  // Auth success: render protected page/component
  return <>{children}</>;
};

export default ProtectedRoute;
