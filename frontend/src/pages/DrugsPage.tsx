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
  const [concentrationFilter, setConcentrationFilter] = useState("");
  const [concentrationOperator, setConcentrationOperator] = useState(">");
  const [volumeFilter, setVolumeFilter] = useState("");
  const [volumeOperator, setVolumeOperator] = useState(">");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDrugs();
  }, []);

  const 548\loadDrugs = async () => {
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
        let result = filtered;
        
        // Фильтрация по концентрации
        if (concentrationFilter) {
          const concentration = parseFloat(concentrationFilter);
          result = result.filter(d => 
            concentrationOperator === ">" 
              ? d.concentration > concentration 
              : d.concentration < concentration
          );
        }
        
        // Фильтрация по объёму
        if (volumeFilter) {
          const volume = parseFloat(volumeFilter);
          result = result.filter(d => 
            volumeOperator === ">" 
              ? d.volume > volume 
              : d.volume < volume
          );
        }
        
        setDrugs(result);
      } else {
        // Фильтрация mock данных
        let result = mockDrugs;
        if (searchName) {
          result = result.filter(d => 
            d.name.toLowerCase().includes(searchName.toLowerCase())
          );
        }
        if (concentrationFilter) {
          const concentration = parseFloat(concentrationFilter);
          result = result.filter(d => 
            concentrationOperator === ">" 
              ? d.concentration > concentration 
              : d.concentration < concentration
          );
        }
        if (volumeFilter) {
          const volume = parseFloat(volumeFilter);
          result = result.filter(d => 
            volumeOperator === ">" 
              ? d.volume > volume 
              : d.volume < volume
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
      if (concentrationFilter) {
        const concentration = parseFloat(concentrationFilter);
        result = result.filter(d => 
          concentrationOperator === ">" 
            ? d.concentration > concentration 
            : d.concentration < concentration
        );
      }
      if (volumeFilter) {
        const volume = parseFloat(volumeFilter);
        result = result.filter(d => 
          volumeOperator === ">" 
            ? d.volume > volume 
            : d.volume < volume
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
          <div className="filter-group">
            <select 
              className="operator-select"
              value={concentrationOperator}
              onChange={(e) => setConcentrationOperator(e.target.value)}
            >
              <option value=">">&gt;</option>
              <option value="<">&lt;</option>
            </select>
            <input
              type="number"
              step="0.01"
              placeholder="Концентрация (мг/мл)"
              className="search-input filter-input"
              value={concentrationFilter}
              onChange={(e) => setConcentrationFilter(e.target.value)}
            />
          </div>
          <div className="filter-group">
            <select 
              className="operator-select"
              value={volumeOperator}
              onChange={(e) => setVolumeOperator(e.target.value)}
            >
              <option value=">">&gt;</option>
              <option value="<">&lt;</option>
            </select>
            <input
              type="number"
              step="0.1"
              placeholder="Объём ампулы (мл)"
              className="search-input filter-input"
              value={volumeFilter}
              onChange={(e) => setVolumeFilter(e.target.value)}
            />
          </div>
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
