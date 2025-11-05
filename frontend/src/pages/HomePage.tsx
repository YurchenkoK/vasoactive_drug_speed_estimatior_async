/* pages/HomePage.tsx */
import { Link } from "react-router-dom";
import "./HomePage.css";

export default function HomePage() {
  return (
    <div className="home-wrapper">
      <div className="home-container">
        <h1 className="home-title">Вазоактивные препараты Pfizer</h1>
        <p className="home-description">
          Сервис для расчёта скорости инфузии вазоактивных препаратов
        </p>
        <Link to="/drugs" className="home-button">
          Перейти к каталогу
        </Link>
      </div>
    </div>
  );
}
