import { useState, useEffect } from "react";
import { MapPin, Send, CheckCircle, X } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

import {
  SEARCH_DB,
  findNearestZone,
  CUSTOM_LOCATION_ID,
  isCustomZone,
} from "../data/search-db";
import type { Zone } from "../data/types";

interface FieldReportFormProps {
  isOpen: boolean;
  onClose: () => void;
  onReportSubmitted?: () => void;
}

export default function FieldReportForm({
  isOpen,
  onClose,
  onReportSubmitted,
}: FieldReportFormProps) {
  if (!isOpen) return null;

  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [location, setLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [locationError, setLocationError] = useState<string | null>(null);
  const [placeName, setPlaceName] = useState<string | null>(null);
  const [reverseGeocoding, setReverseGeocoding] = useState(false);

  const [form, setForm] = useState({
    zone_id: "" as string,
    reporter_id: "",
    crack_width: "",
    seepage: false,
    vegetation: "",
    notes: "",
  });

  // When location is captured, auto-select nearest zone + reverse geocode
  useEffect(() => {
    if (!location) return;

    // Auto-select nearest predefined zone
    const nearest = findNearestZone(location.lat, location.lng);
    if (nearest) {
      setForm((prev) => ({ ...prev, zone_id: nearest.id }));
    }

    // Reverse geocode via Nominatim to show place name
    setReverseGeocoding(true);
    fetch(
      `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${location.lat}&lon=${location.lng}&accept-language=en`,
      { headers: { "Accept-Language": "en" } }
    )
      .then((r) => r.json())
      .then((data) => {
        setPlaceName(data?.display_name || null);
        setReverseGeocoding(false);
      })
      .catch(() => {
        setReverseGeocoding(false);
      });
  }, [location]);

  const handleGetLocation = async () => {
    setError(null);
    setPlaceName(null);
    if (!navigator.geolocation) {
      setLocationError("Geolocation not supported by your browser.");
      return;
    }
    setLoading(true);
    try {
      const pos = await new Promise<GeolocationPosition>((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 60000,
        });
      });
      setLocation({
        lat: pos.coords.latitude,
        lng: pos.coords.longitude,
      });
    } catch (err: any) {
      setLocationError(err.message || "Unable to retrieve location.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!location) {
      setError("Please capture your location first.");
      return;
    }
    if (!form.reporter_id) {
      setError("Please enter your reporter ID.");
      return;
    }

    // For custom locations, send the raw GPS coords. For predefined zones,
    // the backend /reports endpoint still uses the lat/lng we send (not the
    // zone's stored centroid), so this works for both.
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/reports`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          longitude: location.lng,
          latitude: location.lat,
          zone_id: isCustomZone(form.zone_id) ? null : parseInt(form.zone_id, 10),
          reporter_id: form.reporter_id,
          crack_width: form.crack_width ? parseFloat(form.crack_width) : undefined,
          seepage: form.seepage,
          vegetation: form.vegetation || undefined,
          notes: form.notes || undefined,
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Submission failed" }));
        throw new Error(err.detail || "Submission failed");
      }
      setSubmitted(true);
      onReportSubmitted?.();
    } catch (err: any) {
      setError(err.message || "Submission failed. Try again.");
    } finally {
      setLoading(false);
    }
  };

  // Build zone options: predefined zones + optional custom location
  const zoneOptions = [
    ...SEARCH_DB.filter((z) => !z.isHistorical),
    ...(location
      ? [
          {
            id: CUSTOM_LOCATION_ID,
            name: `Custom Location (${location.lat.toFixed(4)}, ${location.lng.toFixed(4)})`,
            lat: location.lat,
            lng: location.lng,
            type: "Anywhere",
          } as Zone,
        ]
      : []),
  ];

  const selectedZone = zoneOptions.find((z) => z.id === form.zone_id);
  const isCustom = isCustomZone(form.zone_id);

  return (
    <>
      <div
        className="fixed inset-0 z-[100] flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
        onClick={onClose}
      >
        <div
          className="glass-panel rounded-[2rem] p-7 w-full max-w-md shadow-2xl border border-white/10"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex justify-between items-start mb-6">
            <h3 className="text-xl font-black text-white tracking-tight">
              Submit Field Report
            </h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-white bg-white/5 hover:bg-white/10 p-2 rounded-full transition-colors"
            >
              <X size={16} />
            </button>
          </div>

          {submitted ? (
            <div className="space-y-4 text-center">
              <div className="w-12 h-12 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-4 border border-emerald-500/30">
                <CheckCircle size={28} className="text-emerald-400" />
              </div>
              <h3 className="text-xl font-black text-white">Report Submitted</h3>
              <p className="text-sm text-gray-300">
                Your field observation has been recorded. Report ID:{" "}
                <span className="font-mono text-emerald-400">#{form.reporter_id}</span>
              </p>
              <button
                onClick={() => {
                  setSubmitted(false);
                  setForm({
                    zone_id: "",
                    reporter_id: "",
                    crack_width: "",
                    seepage: false,
                    vegetation: "",
                    notes: "",
                  });
                  setLocation(null);
                  setPlaceName(null);
                }}
                className="w-full py-3 bg-emerald-500 hover:bg-emerald-400 text-black font-black rounded-2xl text-xs uppercase tracking-widest transition-colors"
              >
                Submit Another
              </button>
            </div>
          ) : (
            <>
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Location Capture */}
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest flex items-center gap-2">
                    <MapPin size={14} className="text-blue-400" /> Location
                  </label>
                  <button
                    onClick={handleGetLocation}
                    disabled={loading}
                    className="w-full bg-black/40 border border-white/10 rounded-2xl py-3 px-4 text-left text-sm font-semibold text-white hover:bg-white/10 transition-colors flex items-center gap-3 disabled:opacity-50"
                  >
                    {loading ? (
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.8)] animate-pulse" />
                        {location
                          ? `Captured: ${location.lat.toFixed(4)}, ${location.lng.toFixed(4)}`
                          : "Capture GPS Location"}
                      </div>
                    )}
                  </button>
                  {locationError && (
                    <p className="text-[10px] text-red-400 font-bold">{locationError}</p>
                  )}
                  {location && (
                    <>
                      <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">
                        Lat: {location.lat.toFixed(6)} • Lng: {location.lng.toFixed(6)}
                      </p>
                      {reverseGeocoding && (
                        <p className="text-[10px] text-blue-400 font-bold animate-pulse">Looking up place…</p>
                      )}
                      {placeName && (
                        <p className="text-[10px] text-emerald-400 font-bold">
                          {placeName}
                        </p>
                      )}
                      {selectedZone && !isCustom && (
                        <p className="text-[10px] text-orange-400 font-bold uppercase tracking-widest">
                          Nearest zone: {selectedZone.name} (ZN-{selectedZone.id})
                        </p>
                      )}
                    </>
                  )}
                </div>

                {/* Zone */}
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest">
                    Zone
                  </label>
                  <select
                    value={form.zone_id}
                    onChange={(e) => setForm({ ...form, zone_id: e.target.value })}
                    className="w-full bg-black/40 border border-white/10 rounded-2xl py-3 px-4 text-sm text-white focus:outline-none focus:border-red-500/50"
                  >
                    <option value="">Select a zone</option>
                    {zoneOptions.map((z) => (
                      <option key={z.id} value={z.id}>
                        {z.name}
                      </option>
                    ))}
                  </select>
                  {isCustom && (
                    <p className="text-[10px] text-yellow-400 font-bold uppercase tracking-widest">
                      Custom location — report will use your GPS coordinates
                    </p>
                  )}
                </div>

                {/* Reporter ID */}
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest">
                    Reporter ID
                  </label>
                  <input
                    type="text"
                    placeholder="e.g., FIELD-001"
                    value={form.reporter_id}
                    onChange={(e) => setForm({ ...form, reporter_id: e.target.value })}
                    className="w-full bg-black/40 border border-white/10 rounded-2xl py-3 px-4 text-sm text-white focus:outline-none focus:border-red-500/50"
                  />
                </div>

                {/* Crack Width */}
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest">
                    Crack Width (mm)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    placeholder="0.0"
                    value={form.crack_width}
                    onChange={(e) => setForm({ ...form, crack_width: e.target.value })}
                    className="w-full bg-black/40 border border-white/10 rounded-2xl py-3 px-4 text-sm text-white focus:outline-none focus:border-red-500/50"
                  />
                </div>

                {/* Seepage */}
                <div className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={form.seepage}
                    onChange={(e) => setForm({ ...form, seepage: e.target.checked })}
                    className="w-4 h-4 rounded bg-black/40 border border-white/10 text-red-500 focus:ring-red-500"
                  />
                  <label className="text-sm font-semibold text-white cursor-pointer">Seepage Observed</label>
                </div>

                {/* Vegetation */}
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest">
                    Vegetation / Soil Condition
                  </label>
                  <select
                    value={form.vegetation}
                    onChange={(e) => setForm({ ...form, vegetation: e.target.value })}
                    className="w-full bg-black/40 border border-white/10 rounded-2xl py-3 px-4 text-sm text-white focus:outline-none focus:border-red-500/50"
                  >
                    <option value="">None specified</option>
                    <option value="bare_soil">Bare Soil</option>
                    <option value="sparse_grass">Sparse Grass</option>
                    <option value="dense_vegetation">Dense Vegetation</option>
                    <option value="exposed_roots">Exposed Roots</option>
                  </select>
                </div>

                {/* Notes */}
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest">
                    Notes
                  </label>
                  <textarea
                    rows={3}
                    placeholder="e.g., New crack near retaining wall, water seeping from base..."
                    value={form.notes}
                    onChange={(e) => setForm({ ...form, notes: e.target.value })}
                    className="w-full bg-black/40 border border-white/10 rounded-2xl py-3 px-4 text-sm text-white focus:outline-none focus:border-red-500/50"
                  />
                </div>

                {error && (
                  <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-3 text-[11px] text-red-400 font-bold">
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading || !location || !form.reporter_id}
                  className="w-full py-4 bg-red-600 hover:bg-red-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors rounded-2xl font-black text-white tracking-widest uppercase text-xs flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(220,38,38,0.4)]"
                >
                  {loading ? (
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <Send size={14} />
                  )}
                  {loading ? "SENDING…" : "SUBMIT FIELD REPORT"}
                </button>
              </form>
            </>
          )}
        </div>
      </div>
    </>
  );
}
