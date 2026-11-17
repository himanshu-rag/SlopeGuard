import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.slopeguard.app',
  appName: 'SlopeGuard',
  webDir: 'dist',
  server: {
    cleartext: false,
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
