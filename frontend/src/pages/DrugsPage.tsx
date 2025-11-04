/* pages/DrugsPage.tsx */
import { useEffect, useState } from "react";
import Breadcrumbs from "../components/Breadcrumbs";
import DrugCard from "../components/DrugCard";
import type { Drug } from "../DrugTypes";
import { listDrugs } from "../drugsApi";
import { mockDrugs } from "../mock/DrugMock";
import "./DrugsPage.css";

export default function DrugsPage() {
  const [drugs, setDrugs] = useState<Drug[]>([]);
  const [searchName, setSearchName] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDrugs();
  }, []);

  const loadDrugs = async () => {
    setLoading(true);
    try {
      const data = await listDrugs();
      if (data.length > 0) {
        setDrugs(data);
      } else {
        setDrugs(mockDrugs);
      }
    } catch {
      setDrugs(mockDrugs);
    }
    setLoading(false);
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const params: any = {};
      if (searchName) params.name = searchName;

      const filtered = await listDrugs(params);
      
      if (filtered.length > 0) {
        setDrugs(filtered);
      } else {
        // Фильтрация mock данных
        let result = mockDrugs;
        if (searchName) {
          result = result.filter(d => 
            d.name.toLowerCase().includes(searchName.toLowerCase())
          );
        }
        setDrugs(result);
      }
    } catch {
      let result = mockDrugs;
      if (searchName) {
        result = result.filter(d => 
          d.name.toLowerCase().includes(searchName.toLowerCase())
        );
      }
      setDrugs(result);
    }
    setLoading(false);
  };

  return (
    <div>
      <div className="breadcrumbs-wrapper">
        <Breadcrumbs items={[
          { label: "Главная", path: "/" },
          { label: "Каталог препаратов" }
        ]} />
      </div>
      <div className="search-section">
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            placeholder="Поиск по названию"
            className="search-input"
            value={searchName}
            onChange={(e) => setSearchName(e.target.value)}
          />
          <button type="submit" className="search-button" disabled={loading}>
            Найти
          </button>
        </form>
      </div>
      
      <div className="container">
        <div className="drugs-grid">
          {drugs.map((drug) => (
            <DrugCard key={drug.id} drug={drug} />
          ))}
        </div>
      </div>
    </div>
  );
}
