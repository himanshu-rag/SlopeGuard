import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.slopeguard.app',
  appName: 'SlopeGuard',
  webDir: 'dist',
  server: {
    url: 'http://10.0.2.2:8000',  // Android emulator localhost
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
      style: 'LIGHT',
    },
    Geolocation: {
      // High-accuracy GPS for landslide monitoring
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
