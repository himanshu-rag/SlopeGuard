export interface Zone {
  id: string;
  name: string;
  lat: number;
  lng: number;
  type?: string;
  slope?: number;
  aspect?: number;
  curvature?: number;
  twi?: number;
  isHistorical?: boolean;
  eventName?: string;
}
