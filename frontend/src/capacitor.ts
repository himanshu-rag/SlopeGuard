import {
  Capacitor,
  type PluginListenerHandle,
} from '@capacitor/core';
import { StatusBar } from '@capacitor/status-bar';
import { SplashScreen } from '@capacitor/splash-screen';
import { Geolocation } from '@capacitor/geolocation';
import { Device } from '@capacitor/device';
import { Network } from '@capacitor/network';
import { LocalNotifications } from '@capacitor/local-notifications';
import {
  Camera,
  CameraResultType,
  CameraSource,
} from '@capacitor/camera';

/**
 * Capacitor service — bridges the web UI to native Android APIs.
 * Falls back gracefully to web APIs when running in a browser.
 */

export interface CapacitorPosition {
  latitude: number;
  longitude: number;
  accuracy: number;
  timestamp: number;
}

export interface NetworkStatus {
  connected: boolean;
  connectionType: 'wifi' | 'cellular' | 'none' | 'unknown';
}

let networkListener: PluginListenerHandle | null = null;
let networkStatusCallback: ((status: NetworkStatus) => void) | null = null;

/**
 * Initialize native plugins (status bar, splash screen, etc.)
 * Call once on app startup.
 */
export async function initCapacitor() {
  if (!Capacitor.isNativePlatform()) return;

  try {
    // Status bar — dark theme to match the app
    await StatusBar.setBackgroundColor({ color: '#0a0a0a' });
    await StatusBar.setStyle({ style: 'dark' as any });

    // Hide splash screen after web app loads
    await SplashScreen.hide();

    // Request geolocation permissions up front
    await Geolocation.requestPermissions();
  } catch (e) {
    console.warn('[Capacitor] Init warning:', e);
  }
}

/**
 * Get high-accuracy GPS position using native Android APIs.
 * Falls back to web geolocation in browser.
 */
export async function getCurrentPosition(): Promise<CapacitorPosition> {
  if (Capacitor.isNativePlatform()) {
    try {
      const pos = await Geolocation.getCurrentPosition({
        enableHighAccuracy: true,
        timeout: 15000,
      });
      return {
        latitude: pos.coords.latitude,
        longitude: pos.coords.longitude,
        accuracy: pos.coords.accuracy,
        timestamp: pos.timestamp,
      };
    } catch (e) {
      console.warn('[Capacitor] Native geolocation failed, falling back to web:', e);
    }
  }
  // Web fallback
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation not supported'));
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        resolve({
          latitude: pos.coords.latitude,
          longitude: pos.coords.longitude,
          accuracy: pos.coords.accuracy,
          timestamp: pos.timestamp,
        });
      },
      (err) => reject(err),
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 60000 }
    );
  });
}

/**
 * Capture a photo using the native camera.
 * Returns a base64 data URI for the photo.
 */
export async function capturePhoto(): Promise<string | null> {
  if (!Capacitor.isNativePlatform()) {
    // Web fallback: prompt user to select a file
    return new Promise((resolve) => {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = 'image/*';
      input.onchange = (e) => {
        const file = (e.target as HTMLInputElement).files?.[0];
        if (!file) {
          resolve(null);
          return;
        }
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result as string);
        reader.readAsDataURL(file);
      };
      input.click();
    });
  }

  try {
    const result = await Camera.getPhoto({
      quality: 80,
      allowEditing: false,
      resultType: CameraResultType.DataUrl,
      source: CameraSource.Camera,
      width: 1200,
    });
    return result.dataUrl ?? null;
  } catch (e) {
    console.warn('[Capacitor] Camera error:', e);
    return null;
  }
}

/**
 * Get device info for logging/debugging.
 */
export async function getDeviceInfo() {
  if (!Capacitor.isNativePlatform()) {
    return { platform: 'web', model: 'Browser', osVersion: 'N/A' };
  }

  const info = await Device.getInfo();
  return {
    platform: info.platform,
    model: info.model,
    osVersion: info.osVersion,
    appVersion: (info as any).appVersion ?? 'N/A',
  };
}

/**
 * Subscribe to network connectivity changes.
 * Calls the callback with current status immediately, then on changes.
 */
export function onNetworkStatusChange(
  callback: (status: NetworkStatus) => void
): () => void {
  networkStatusCallback = callback;

  // Initial check
  Network.getStatus().then((status: any) => {
    networkStatusCallback?.(mapNetworkStatus(status));
  });

  if (Capacitor.isNativePlatform()) {
    Network.addListener('networkStatusChange', (status: any) => {
      networkStatusCallback?.(mapNetworkStatus(status));
    }).then((handle) => {
      networkListener = handle;
    });
  }

  return () => {
    networkListener?.remove();
    networkListener = null;
    networkStatusCallback = null;
  };
}

function mapNetworkStatus(status: any): NetworkStatus {
  const connectionType = status.connectionType?.toLowerCase() || 'unknown';
  return {
    connected: status.connected !== false,
    connectionType:
      connectionType === 'wifi'
        ? 'wifi'
        : connectionType === 'cellular'
          ? 'cellular'
          : connectionType === 'none'
            ? 'none'
            : 'unknown',
  };
}

/**
 * Show a local notification (for CRITICAL risk alerts).
 * Works on Android without Firebase setup.
 */
export async function showCriticalAlert({
  title,
  body,
  zoneName,
}: {
  title: string;
  body: string;
  zoneName: string;
}) {
  if (!Capacitor.isNativePlatform()) {
    // Browser fallback: standard notification
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(title, { body, icon: '/icons.svg' });
    }
    return;
  }

  try {
    await LocalNotifications.schedule({
      notifications: [
        {
          id: Date.now(),
          title,
          body,
          smallIcon: 'ic_stat_notification',
          iconColor: '#EF4444',
          sound: 'beep.wav',
          extra: { zoneName, type: 'CRITICAL_ALERT' },
        },
      ],
    });
  } catch (e) {
    console.warn('[Capacitor] Local notification failed:', e);
  }
}

/**
 * Request notification permissions (Android 13+).
 */
export async function requestNotificationPermissions() {
  if (!Capacitor.isNativePlatform()) return;
  try {
    await LocalNotifications.requestPermissions();
  } catch (e) {
    console.warn('[Capacitor] Notification permission request failed:', e);
  }
}

/**
 * Hide the native splash screen (call after app is ready).
 */
export async function hideSplashScreen() {
  if (Capacitor.isNativePlatform()) {
    try {
      await SplashScreen.hide();
    } catch (e) {
      console.warn('[Capacitor] Splash screen hide failed:', e);
    }
  }
}

/**
 * Check if running on a native mobile device.
 */
export function isMobile(): boolean {
  return Capacitor.isNativePlatform();
}
