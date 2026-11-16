import Map, { Source, Layer } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';

interface MapViewProps {
  viewState: any;
  baseMap: 'dark' | 'satellite';
  showTerrainLayer: boolean;
  showFieldReports: boolean;
  currentZone: any;
  evacuationRoute: any;
  onMove: (evt: any) => void;
}

const osmStyle = {
  version: 8,
  sources: { 'osm': { type: 'raster', tiles: ['https://a.tile.openstreetmap.org/{z}/{x}/{y}.png', 'https://b.tile.openstreetmap.org/{z}/{x}/{y}.png', 'https://c.tile.openstreetmap.org/{z}/{x}/{y}.png'], tileSize: 256, attribution: '&copy; OpenStreetMap Contributors' } },
  layers: [{ id: 'osm-layer', type: 'raster', source: 'osm', minzoom: 0, maxzoom: 19 }]
};

const satelliteStyle = {
  version: 8,
  sources: {
    'satellite': { type: 'raster', tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'], tileSize: 256, attribution: '&copy; Esri' },
    'labels': { type: 'raster', tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}'] }
  },
  layers: [
    { id: 'satellite-layer', type: 'raster', source: 'satellite', minzoom: 0 },
    { id: 'labels-layer', type: 'raster', source: 'labels', minzoom: 0 }
  ]
};

export default function MapView({
  viewState,
  baseMap,
  showTerrainLayer,
  showFieldReports,
  currentZone,
  evacuationRoute,
  onMove,
}: MapViewProps) {
  const d = 0.015;
  const dynamicTerrain = {
    type: 'FeatureCollection',
    features: [{ type: 'Feature', geometry: { type: 'Polygon', coordinates: [[[currentZone.lng - d, currentZone.lat - d], [currentZone.lng + d, currentZone.lat - d], [currentZone.lng + d, currentZone.lat + d], [currentZone.lng - d, currentZone.lat + d], [currentZone.lng - d, currentZone.lat - d]]] } }]
  };

  const dynamicReports = {
    type: 'FeatureCollection',
    features: [
      { type: 'Feature', geometry: { type: 'Point', coordinates: [currentZone.lng - 0.005, currentZone.lat + 0.005] } },
      { type: 'Feature', geometry: { type: 'Point', coordinates: [currentZone.lng + 0.008, currentZone.lat - 0.002] } }
    ]
  };

  const dynamicNodes = {
    type: 'FeatureCollection',
    features: [
      { type: 'Feature', geometry: { type: 'Point', coordinates: [currentZone.lng - 0.003, currentZone.lat + 0.005] }, properties: { name: 'NODE-Alpha', status: 'online' } },
      { type: 'Feature', geometry: { type: 'Point', coordinates: [currentZone.lng + 0.001, currentZone.lat + 0.001] }, properties: { name: 'NODE-Beta', status: 'online' } },
      { type: 'Feature', geometry: { type: 'Point', coordinates: [currentZone.lng + 0.004, currentZone.lat - 0.004] }, properties: { name: 'NODE-Gamma', status: 'offline' } }
    ]
  };

  return (
    <div className={`absolute inset-0 z-0 ${baseMap === 'dark' ? 'dark-map-layer' : ''}`}>
      <Map
        {...viewState}
        onMove={onMove}
        mapStyle={baseMap === 'dark' ? osmStyle as any : satelliteStyle as any}
        style={{ width: '100%', height: '100%' }}
      >
        {showTerrainLayer && (
          <Source id="terrain" type="geojson" data={dynamicTerrain as any}>
            <Layer id="terrain-fill" type="fill" paint={{ 'fill-color': '#ef4444', 'fill-opacity': 0.3 }} />
            <Layer id="terrain-line" type="line" paint={{ 'line-color': '#ef4444', 'line-width': 2, 'line-dasharray': [2, 2] }} />
          </Source>
        )}

        {showFieldReports && (
          <Source id="reports" type="geojson" data={dynamicReports as any}>
            <Layer id="reports-circle" type="circle" paint={{ 'circle-radius': 8, 'circle-color': '#3b82f6', 'circle-stroke-width': 3, 'circle-stroke-color': '#ffffff' }} />
          </Source>
        )}

        <Source id="iot-nodes" type="geojson" data={dynamicNodes as any}>
          <Layer id="nodes-circle" type="circle" paint={{ 'circle-radius': 6, 'circle-color': ['match', ['get', 'status'], 'online', '#22c55e', '#ef4444', '#ef4444'], 'circle-stroke-width': 2, 'circle-stroke-color': '#000000' }} />
          <Layer id="nodes-label" type="symbol" layout={{ 'text-field': ['get', 'name'], 'text-size': 11, 'text-offset': [0, 1.2], 'text-anchor': 'top' }} paint={{ 'text-color': '#ffffff', 'text-halo-color': '#000000', 'text-halo-width': 2 }} />
        </Source>

        {evacuationRoute && (
          <Source id="evac-route" type="geojson" data={evacuationRoute}>
            <Layer id="evac-route-glow" type="line" filter={['==', 'type', 'route']} paint={{ 'line-color': '#eab308', 'line-width': 8, 'line-opacity': 0.4, 'line-blur': 4 }} />
            <Layer id="evac-route-line" type="line" filter={['==', 'type', 'route']} paint={{ 'line-color': '#eab308', 'line-width': 3, 'line-dasharray': [2, 2] }} />
            <Layer id="safe-zone-circle" type="circle" filter={['==', 'type', 'safezone']} paint={{ 'circle-radius': 12, 'circle-color': '#10b981', 'circle-stroke-width': 3, 'circle-stroke-color': '#ffffff' }} />
            <Layer id="safe-zone-label" type="symbol" filter={['==', 'type', 'safezone']} layout={{ 'text-field': ['get', 'name'], 'text-size': 12, 'text-offset': [0, 1.5], 'text-anchor': 'top' }} paint={{ 'text-color': '#ffffff', 'text-halo-color': '#000000', 'text-halo-width': 2 }} />
          </Source>
        )}
      </Map>
    </div>
  );
}