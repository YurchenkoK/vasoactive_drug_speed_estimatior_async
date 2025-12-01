import { useEffect, useState } from "react";
import { useCart } from "../CartContext";
import { useSelector, useDispatch } from "react-redux";
import Breadcrumbs from "../components/Breadcrumbs";
import DrugCard from "../components/DrugCard";
import type { Drug } from "../DrugTypes";
import { listDrugs } from "../drugsApi";
import { mockDrugs } from "../mock/DrugMock";
import type { RootState } from "../store";
import { setName } from "../features/drugsFilter/filterSlice";
import "./DrugsPage.css";
import CartButton from "../components/CartButton";

export default function DrugsPage() {
  const dispatch = useDispatch();
  const searchName = useSelector((state: RootState) => state.drugsFilter.name);
  const { fetchOnPageEnter } = useCart();
  

  const [drugs, setDrugs] = useState<Drug[]>([]);
  const [loading, setLoading] = useState(false);
  const [notFound, setNotFound] = useState(false);

  const fetchDrugs = async (filter?: { name?: string; concentration_min?: number; concentration_max?: number }) => {
    setLoading(true);
    try {
      const data = await listDrugs(filter);
      if (data && data.length > 0) {
        setDrugs(data);
        setNotFound(false);
      } else {
        const mockFiltered = mockDrugs.filter((d) => {
          let matches = true;
          if (filter?.name) {
            matches = matches && d.name.toLowerCase().includes(filter.name.toLowerCase());
          }
          if (filter?.concentration_min !== undefined && filter?.concentration_min !== null) {
            matches = matches && d.concentration >= filter.concentration_min;
          }
          if (filter?.concentration_max !== undefined && filter?.concentration_max !== null) {
            matches = matches && d.concentration <= filter.concentration_max;
          }
          return matches;
        });
        setDrugs(mockFiltered);
        setNotFound(mockFiltered.length === 0);
      }
    } catch {
      const mockFiltered = mockDrugs.filter((d) => {
        let matches = true;
        if (filter?.name) {
          matches = matches && d.name.toLowerCase().includes(filter.name.toLowerCase());
        }
        if (filter?.concentration_min !== undefined && filter?.concentration_min !== null) {
          matches = matches && d.concentration >= filter.concentration_min;
        }
        if (filter?.concentration_max !== undefined && filter?.concentration_max !== null) {
          matches = matches && d.concentration <= filter.concentration_max;
        }
        return matches;
      });
      setDrugs(mockFiltered);
      setNotFound(mockFiltered.length === 0);
    } finally {
      setLoading(false);
    }
  };


  const handleSearch = () => {
    const filter: any = {};
    if (searchName) filter.name = searchName;
    fetchDrugs(Object.keys(filter).length > 0 ? filter : undefined);
  };

  useEffect(() => {
    const filter: any = {};
    if (searchName) filter.name = searchName;
    fetchDrugs(Object.keys(filter).length > 0 ? filter : undefined);
    // refresh cart info when entering the page and log it
    (async () => {
      try {
        await fetchOnPageEnter();
      } catch (e) {
        // fail silently
      }
    })();
  }, []);

  return (
    <div>
      <div className="breadcrumbs-wrapper">
        <Breadcrumbs items={[
          { label: "Главная", path: "/" },
          { label: "Каталог препаратов" }
        ]} />
      </div>
      <div className="search-section">
        <div className="search-form">
          <input
            type="text"
            placeholder="Название препарата..."
            className="search-input"
            value={searchName}
            onChange={(e) => dispatch(setName(e.target.value))}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
          <button onClick={handleSearch} className="search-button">
            Найти
          </button>
        </div>
      </div>

  {/* Добавленная кнопка корзины на странице каталога */}
  <CartButton />

        {loading ? (
        <div className="loading-container"></div>
      ) : notFound ? (
        <div className="not-found-message">Ничего не найдено</div>
      ) : (
        <div className="container">
          <div className="drugs-grid">
            {drugs.map((drug) => (
              <DrugCard key={drug.id} drug={drug} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
