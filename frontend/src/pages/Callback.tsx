import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import authService from "../services/authService"; // Import the authService

function Callback() {
  const navigate = useNavigate();

  useEffect(() => {
    const processCallback = async () => {
      const success: boolean = authService.handleAuthCallback();

      if (success) {
        navigate("/Home"); // internal route after successful login
      } else {
        console.log("⚠️ Callback failed, redirecting to login");
        // await authService.redirectToLogin(); // redirect to login if callback fails
      }
    };

    processCallback();
  }, [navigate]); // add navigate as dependency

  return <div>Logging in, please wait...</div>;
}

export default Callback;
