import { Link, useNavigate } from "react-router-dom";
import { api } from "../api";

export default function Navbar() {
  const navigate = useNavigate();
  const authed = api.isAuthed();

  function handleLogout() {
    api.logout();
    navigate("/login");
  }

  return (
    <div className="topbar">
      <div className="topbar-inner">
        <Link to="/" className="brand">
          <span className="brand-mark" />
          Fieldnotes
          <span className="brand-tagline">resume ⋄ job match</span>
        </Link>
        <div className="nav-links">
          {authed ? (
            <>
              <Link to="/dashboard">Dashboard</Link>
              <button onClick={handleLogout}>Log out</button>
            </>
          ) : (
            <>
              <Link to="/login">Log in</Link>
              <Link to="/register">Register</Link>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
