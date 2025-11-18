export interface Drug {
  id: number;
  name: string;
  description: string;
  image_url?: string;
  concentration: number;
  volume: number;
  is_active: boolean;
}
