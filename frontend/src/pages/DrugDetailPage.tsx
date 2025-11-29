import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Breadcrumbs from "../components/Breadcrumbs";
import CartButton from "../components/CartButton";
import type { Drug } from "../DrugTypes";
import { getDrug } from "../drugsApi";
import { mockDrugs } from "../mock/DrugMock";
import "./DrugDetailPage.css";

const BASE_URL = import.meta.env.BASE_URL;
const DEFAULT_IMAGE = `${BASE_URL}placeholder-drug.png`;

export default function DrugDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [drug, setDrug] = useState<Drug | null>(null);

  useEffect(() => {
    if (!id) return;

    const loadDrug = async () => {
      try {
        const data = await getDrug(parseInt(id));
        if (data) {
          setDrug(data);
        } else {
          const mockDrug = mockDrugs.find(d => d.id === parseInt(id));
          setDrug(mockDrug || null);
        }
      } catch {
        const mockDrug = mockDrugs.find(d => d.id === parseInt(id));
        setDrug(mockDrug || null);
      }
    };

    loadDrug();
  }, [id]);

  if (!drug) {
    return <div className="loading-container"></div>;
  }

  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement>) => {
    const img = e.currentTarget as HTMLImageElement;
    if (!img.dataset.fallback) {
      img.dataset.fallback = '1';
      img.src = DEFAULT_IMAGE;
    }
  };

  return (
    <div className="container">
      <Breadcrumbs items={[
        { label: "Главная", path: "/" },
        { label: "Каталог препаратов", path: "/drugs" },
        { label: drug.name }
      ]} />
      <div className="drug-detail">
        <div className="drug-detail-image">
          <img 
            src={drug.image_url || DEFAULT_IMAGE}
            alt={drug.name}
            onError={handleImageError}
          />
        </div>
        <div className="drug-detail-info">
          <h2 className="drug-detail-title">{drug.name}</h2>
          <div className="drug-params">
            <p><strong>Концентрация ампулы:</strong> {drug.concentration} мг/мл</p>
            <p><strong>Объём ампулы:</strong> {drug.volume} мл</p>
            <p><strong>Показания:</strong> {drug.description}</p>
          </div>
        </div>
      </div>
        {/* Фиксированная кнопка корзины внизу слева на странице с товаром */}
        <CartButton />
    </div>
  );
}
