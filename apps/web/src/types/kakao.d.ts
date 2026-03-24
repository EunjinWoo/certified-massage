declare global {
  interface Window {
    kakao?: {
      maps: {
        LatLng: new (lat: number, lng: number) => unknown;
        LatLngBounds: new () => {
          extend: (latLng: unknown) => void;
        };
        Map: new (
          container: HTMLElement,
          options: {
            center: unknown;
            level: number;
          }
        ) => {
          setCenter: (position: unknown) => void;
          setBounds: (bounds: unknown) => void;
        };
        Marker: new (options: { position: unknown }) => {
          setMap: (map: unknown | null) => void;
        };
        InfoWindow: new (options: { content: string }) => {
          open: (map: unknown, marker: unknown) => void;
        };
        event: {
          addListener: (
            target: unknown,
            eventName: string,
            handler: () => void
          ) => void;
        };
        load: (callback: () => void) => void;
      };
    };
  }
}

export {};
