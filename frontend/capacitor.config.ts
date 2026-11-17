import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.slopeguard.app',
  appName: 'SlopeGuard',
  webDir: 'dist',
  server: {
    // For Android emulator: http://10.0.2.2:8000
    // For real device: use your computer's LAN IP (e.g., http://192.168.1.50:8000)
    url: process.env.CAPACITOR_SERVER_URL ?? 'http://10.154.148.46:8000',
    cleartext: true,
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: '#0a0a0a',
      androidSplashResourceName: 'splash',
      androidScaleType: 'CENTER_CROP',
    },
    StatusBar: {
      backgroundColor: '#0a0a0a',
      style: 'DARK',
    },
    Geolocation: {
      androidForceLocationManager: true,
    },
    LocalNotifications: {
      smallIcon: 'ic_stat_notification',
      iconColor: '#EF4444',
      sound: 'beep.wav',
    },
  },
};

export default config;
