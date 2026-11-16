import type { Zone } from "./types";

export const SEARCH_DB: Zone[] = [
  { id: '2', name: 'Shimla, HP',      lat: 31.1048, lng: 77.1734, type: 'Himalayan Slopes',  slope: 55.0, aspect: 220.0, curvature: -0.8, twi: 5.2 },
  { id: '3', name: 'Darjeeling, WB',  lat: 27.0360, lng: 88.2627, slope: 48.0, aspect: 160.0, curvature: -0.3, twi: 6.1, type: 'Steep Tea Estates' },
  { id: '4', name: 'Munnar, KL',      lat: 10.0889, lng: 77.0595, slope: 35.0, aspect: 270.0, curvature:  0.2, twi: 8.5, type: 'Western Ghats' },
  { id: '5', name: 'Guwahati, AS',    lat: 26.1400, lng: 91.7600, slope: 45.0, aspect: 140.0, curvature: -0.5, twi: 8.2, type: 'Urban Hills' },
  { id: 'wayanad_1', name: 'Wayanad, KL (2024)', lat: 11.5549, lng: 76.0822, slope: 62.0, aspect: 180, curvature: -0.9, twi: 12.5, type: 'Historical Event', isHistorical: true, eventName: '2024 Wayanad' },
  { id: 'kedar_1', name: 'Kedarnath, UK (2013)', lat: 30.7352, lng: 79.0669, slope: 75.0, aspect: 220, curvature: -1.2, twi: 14.0, type: 'Historical Event', isHistorical: true, eventName: '2013 Kedarnath' },
];

/**
 * Haversine distance between two points (km).
 */
export function haversineKm(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371;
  const toRad = (d: number) => (d * Math.PI) / 180;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

/**
 * Find the nearest predefined zone to a given lat/lng.
 * Returns null if SEARCH_DB is empty.
 */
export function findNearestZone(lat: number, lng: number): Zone | null {
  if (SEARCH_DB.length === 0) return null;
  let best: Zone | null = null;
  let bestDist = Infinity;
  for (const z of SEARCH_DB) {
    const d = haversineKm(lat, lng, z.lat, z.lng);
    if (d < bestDist) {
      bestDist = d;
      best = z;
    }
  }
  return best;
}

/**
 * Special "custom location" marker id used when the user submits from
 * an arbitrary GPS point that isn't near any predefined zone.
 */
export const CUSTOM_LOCATION_ID = "custom";

export function isCustomZone(id: string | undefined): boolean {
  return id === CUSTOM_LOCATION_ID;
}
