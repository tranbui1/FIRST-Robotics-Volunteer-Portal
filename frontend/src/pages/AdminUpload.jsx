import { useState, useEffect } from "react";

/**
 * AdminUpload Component
 * --------------------
 * This component provides a secure interface for admins to:
 *   - Log in using a password
 *   - Upload Match Data CSV
 *   - Upload Role Links CSV
 *   - Track upload activity and session expiration
 *   - Logout
 *
 * State:
 *   - password: Admin password input
 *   - sessionToken: Auth token after login
 *   - sessionExpires: Token expiration timestamp
 *   - matchFile: Selected CSV for match data
 *   - roleFile: Selected CSV for role links
 *   - response: Activity log messages
 *   - loading: Tracks ongoing async operations
 */
export default function AdminUpload() {
  const [password, setPassword] = useState("");           
  const [sessionToken, setSessionToken] = useState(null); 
  const [sessionExpires, setSessionExpires] = useState(null); 
  const [matchFile, setMatchFile] = useState(null);       
  const [roleFile, setRoleFile] = useState(null);         
  const [response, setResponse] = useState("");           
  const [loading, setLoading] = useState(false);          

  // Check session expiration every minute 
  useEffect(() => {
    if (sessionExpires) {
      const checkExpiration = () => {
        if (new Date() > new Date(sessionExpires)) {
          setSessionToken(null);
          setSessionExpires(null);
          alert("Session expired. Please login again.");
        }
      };
      const interval = setInterval(checkExpiration, 60000);
      return () => clearInterval(interval);
    }
  }, [sessionExpires]);

  // Handle admin login
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await fetch("http://localhost:5001/api/admin-login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });

      const data = await res.json();

      if (res.ok) {
        setSessionToken(data.session_token);    
        setSessionExpires(data.expires_at);     
        setPassword("");                         
        setResponse("Login successful!");
      } else {
        alert(data.error || "Login failed");
      }
    } catch (err) {
      alert("Login failed: ", err.message);
    } finally {
      setLoading(false);
    }
  };

  // Generic file upload function 
  const uploadFile = async (file, endpoint, fileType) => {
    if (!file) {
      alert(`No ${fileType} file selected`);
      return;
    }

    if (!file.name.endsWith('.csv')) {
      alert("Only CSV files are allowed");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`http://localhost:5001${endpoint}`, {
        method: "POST",
        headers: { "X-Admin-Token": sessionToken },
        body: formData,
      });

      const data = await res.json();

      if (res.ok) {
        setResponse(prev => `${prev}\n ${fileType}: ${data.message}`);
        if (fileType === "Match Data") setMatchFile(null);
        if (fileType === "Role Links") setRoleFile(null);
      } else {
        setResponse(prev => `${prev}\n ${fileType}: ${data.error}`);
      }
    } catch (err) {
      setResponse(prev => `${prev}\n ${fileType} upload failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Logout function 
  const handleLogout = () => {
    setSessionToken(null);
    setSessionExpires(null);
    setPassword("");
    setMatchFile(null);
    setRoleFile(null);
    setResponse("");
  };

  // Display remaining session time
  const getTimeRemaining = () => {
    if (!sessionExpires) return "";

    const now = new Date();
    const expires = new Date(sessionExpires);
    const diff = expires - now;

    if (diff <= 0) return "Expired";

    const minutes = Math.floor(diff / 60000);
    return `${minutes} minutes remaining`;
  };

  // Login form if not logged in 
  if (!sessionToken) {
    return (
      <div>
        <h2>Admin Login</h2>
        <p>Enter the admin password</p>
        <div>
          <input
            type="password"
            placeholder="Enter admin password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleLogin(e)}
            disabled={loading} 
          />
          <button onClick={handleLogin} disabled={loading}>
            {loading ? "Logging in..." : "Login"}
          </button>
        </div>
      </div>
    );
  }

  // Admin upload panel UI 
  return (
    <div>
      <div>
        <h1>Admin Upload</h1>
        <p>Upload CSV files to update system data</p>
        <div>
          <span>Session: {getTimeRemaining()}</span>
          <button onClick={handleLogout}>Logout</button>
        </div>
      </div>

      <div>
        <br />
        <h2>File Uploads</h2>
        <br />

        {/* Match Data Upload */}
        <div>
          <h3>Match Data CSV</h3>
          <br />
          <input
            type="file"
            accept=".csv"
            onChange={(e) => setMatchFile(e.target.files[0])}
          />
          <button
            onClick={() => uploadFile(matchFile, "/api/upload-match-data", "Match Data")}
            disabled={!matchFile || loading}
          >
            {loading ? "Uploading..." : "Upload Match Data"}
          </button>
          {matchFile && <p>Selected: {matchFile.name}</p>}
        </div>

        {/* Role Links Upload */}
        <div>
          <br />
          <h3>Role Links CSV</h3>
          <br />
          <input
            type="file"
            accept=".csv"
            onChange={(e) => setRoleFile(e.target.files[0])}
          />
          <button
            onClick={() => uploadFile(roleFile, "/api/upload-role-links", "Role Links")}
            disabled={!roleFile || loading}
          >
            {loading ? "Uploading..." : "Upload Role Links"}
          </button>
          {roleFile && <p>Selected: {roleFile.name}</p>}
        </div>
      </div>

      {/* Activity log */}
      {response && (
        <div>
          <br />
          <h2>Activity Log</h2>
          <button onClick={() => setResponse("")}>Clear Log</button>
          <pre>{response}</pre>
        </div>
      )}
    </div>
  );
}
