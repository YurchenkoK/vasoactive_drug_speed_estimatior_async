import { Link } from "react-router-dom";
import Carousel from "../components/Carousel";
import "./HomePage.css";

const drugImages = [
  "/EpiVial.jpg",
  "/Milrinonepackvial.png",
  "/nitroglic.jpg",
  "/phenylephirine.jpg",
];

export default function HomePage() {
  return (
    <div className="home-wrapper">
      <div className="home-container">
        <h1 className="home-title">Вазоактивные препараты Pfizer</h1>
        <p className="home-description">
          Сервис для расчёта скорости инфузии вазоактивных препаратов
        </p>
        
        <div className="home-carousel-section">
          <Carousel images={drugImages} autoPlayInterval={12000} />
        </div>

        <Link to="/drugs" className="home-button">
          Перейти к каталогу
        </Link>
      </div>
    </div>
  );
}
