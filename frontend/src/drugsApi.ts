import type { Drug } from "./DrugTypes";

const isTauri = typeof window !== 'undefined' && '__TAURI__' in window;

const API_BASE_URL = isTauri 
  ?'http://192.168.1.240:8000':'';

export async function listDrugs(params?: { 
  name?: string; 
  concentration_min?: number;
  concentration_max?: number;
}): Promise<Drug[]> {
  try {
    let path = `${API_BASE_URL}/api/drugs/`;
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
    const res = await fetch(`${API_BASE_URL}/api/drugs/${id}/`, { headers: { Accept: "application/json" } });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn("[API] error fetching drug", err);
    return null;
  }
}

export interface CartInfo {
  order_id: number;
  count: number;
}

export async function getCartInfo(): Promise<CartInfo> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/orders/cart/`, { 
      headers: { Accept: "application/json" },
      credentials: 'include'
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn("[API] error fetching cart info", err);
    return { order_id: 0, count: 0 };
  }
}
