/* pages/DrugDetailPage.tsx */
import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import Breadcrumbs from "../components/Breadcrumbs";
import type { Drug } from "../DrugTypes";
import { getDrug } from "../drugsApi";
import { mockDrugs } from "../mock/DrugMock";
import "./DrugDetailPage.css";

const DEFAULT_IMAGE = "http://localhost:9000/images/placeholder-drug.png";

export default function DrugDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [drug, setDrug] = useState<Drug | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;

    const loadDrug = async () => {
      setLoading(true);
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
      setLoading(false);
    };

    loadDrug();
  }, [id]);

  if (loading) {
    return (
      <div className="loading-container">
        <p>Загрузка...</p>
      </div>
    );
  }

  if (!drug) {
    return (
      <div className="loading-container">
        <h2>Препарат не найден</h2>
        <Link to="/drugs" className="details-button">
          Вернуться к каталогу
        </Link>
      </div>
    );
  }

  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement>) => {
    const img = e.target as HTMLImageElement;
    // Проверяем, не является ли текущий src уже placeholder
    if (img.src !== window.location.origin + DEFAULT_IMAGE) {
      img.src = DEFAULT_IMAGE;
      // Удаляем обработчик, чтобы избежать повторных вызовов
      img.onerror = null;
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
            <div className="drug-detail-form">
              <Link to="/drugs" className="details-button">
                ← Назад к каталогу
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
