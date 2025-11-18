import type { Drug } from "./DrugTypes";

export async function listDrugs(params?: { 
  name?: string; 
  concentration_min?: number;
  concentration_max?: number;
}): Promise<Drug[]> {
  try {
    let path = "/api/drugs/";
    if (params) {
      const query = new URLSearchParams();
      if (params.name) query.append("name", params.name);
      if (params.concentration_min) query.append("concentration_min", params.concentration_min.toString());
      if (params.concentration_max) query.append("concentration_max", params.concentration_max.toString());
      const queryString = query.toString();
      if (queryString) path += `?${queryString}`;
    }

    const res = await fetch(path, { headers: { Accept: "application/json" } });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn("[API] error fetching drugs", err);
    return [];
  }
}

export async function getDrug(id: number): Promise<Drug | null> {
  try {
    const res = await fetch(`/api/drugs/${id}/`, { headers: { Accept: "application/json" } });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn("[API] error fetching drug", err);
    return null;
  }
}
