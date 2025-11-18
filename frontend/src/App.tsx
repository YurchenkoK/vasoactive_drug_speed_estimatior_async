import { Routes, Route, useLocation } from "react-router-dom";
import AppNavbar from "./components/AppNavbar";
import CartButton from "./components/CartButton";
import HomePage from "./pages/HomePage";
import DrugsPage from "./pages/DrugsPage";
import DrugDetailPage from "./pages/DrugDetailPage";
import "./App.css";

export default function App() {
  const location = useLocation();
  const isHomePage = location.pathname === "/";

  return (
    <>
      <AppNavbar />
      <div className="app-container">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/drugs" element={<DrugsPage />} />
          <Route path="/drugs/:id" element={<DrugDetailPage />} />
        </Routes>
      </div>
      {!isHomePage && <CartButton count={0} />}
    </>
  );
}
