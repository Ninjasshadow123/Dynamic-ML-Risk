import { NavLink, Outlet } from "react-router-dom";


function Layout() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <div className="brand">
            <div className="brand-mark">MR</div>

            <div>
              <h1>Machine Risk</h1>
              <p>Management Console</p>
            </div>
          </div>

          <nav className="navigation">
            <NavLink
              to="/fields"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              Field Configuration
            </NavLink>

            <NavLink
              to="/machines"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              Machine Records
            </NavLink>

            <NavLink
              to="/prediction"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              Risk Prediction
            </NavLink>
          </nav>
        </div>

        <div className="sidebar-footer">
          <span className="status-dot" />
          Local ML System
        </div>
      </aside>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}


export default Layout;