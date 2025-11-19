import { Link } from "react-router-dom";
import type { Drug } from "../DrugTypes";
import "./DrugCard.css";

interface DrugCardProps {
  drug: Drug;
}

const BASE_URL = import.meta.env.BASE_URL;
const DEFAULT_IMAGE = `${BASE_URL}placeholder-drug.png`;

export default function DrugCard({ drug }: DrugCardProps) {
  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement>) => {
    const img = e.currentTarget as HTMLImageElement;
    if (!img.dataset.fallback) {
      img.dataset.fallback = '1';
      img.src = DEFAULT_IMAGE;
    }
  };

  return (
    <div className="drug-card">
      <img 
        src={drug.image_url || DEFAULT_IMAGE}
        alt={drug.name}
        className="drug-image"
        onError={handleImageError}
      />
      <h3 className="drug-name">{drug.name}</h3>
      <p className="drug-concentration">
        Концентрация в амп.: {drug.concentration} мг/мл
      </p>
      <Link to={`/drugs/${drug.id}`} className="details-button">
        Подробнее
      </Link>
    </div>
  );
}
