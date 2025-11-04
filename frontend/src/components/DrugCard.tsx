/* components/DrugCard.tsx */
import { Link } from "react-router-dom";
import type { Drug } from "../DrugTypes";
import "./DrugCard.css";

interface DrugCardProps {
  drug: Drug;
}

const DEFAULT_IMAGE = "/placeholder-drug.png";

export default function DrugCard({ drug }: DrugCardProps) {
  return (
    <div className="drug-card">
      <img 
        src={drug.image_url || DEFAULT_IMAGE}
        alt={drug.name}
        className="drug-image"
        onError={(e) => {
          (e.target as HTMLImageElement).src = DEFAULT_IMAGE;
        }}
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
