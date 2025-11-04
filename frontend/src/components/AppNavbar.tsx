/* components/AppNavbar.tsx */
import { Link } from "react-router-dom";
import "./AppNavbar.css";

export default function AppNavbar() {
  return (
    <div className="header">
      <div className="header-content">
        <Link to="/">
          <h1 className="logo">Pfizer</h1>
        </Link>
        <Link to="/" className="home-link">
          Главная
        </Link>
      </div>
    </div>
  );
}
