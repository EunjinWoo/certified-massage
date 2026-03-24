"use client";

import { useEffect, useRef, useState } from "react";

import type { Shop } from "@/lib/types";

const DEFAULT_CENTER = {
  lat: 36.3504,
  lng: 127.3845
};

const MAP_CONTAINER_ID = "kakao-map-canvas";

function escapeHtml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function buildInfoWindow(shop: Shop): string {
  return [
    "<div style='padding:12px;max-width:260px;font-family:Segoe UI,sans-serif;'>",
    `<strong style='display:block;margin-bottom:6px;'>${escapeHtml(shop.name)}</strong>`,
    `<div style='font-size:12px;line-height:1.5;'>${escapeHtml(shop.addressNormalized || shop.addressRaw)}</div>`,
    shop.phone
      ? `<div style='font-size:12px;margin-top:6px;'>${escapeHtml(shop.phone)}</div>`
      : "",
    "</div>"
  ].join("");
}

function loadKakaoSdk(appKey: string): Promise<void> {
  return new Promise((resolve, reject) => {
    if (window.kakao?.maps) {
      resolve();
      return;
    }

    const existing = document.querySelector(
      'script[data-kakao-sdk="true"]'
    ) as HTMLScriptElement | null;

    if (existing) {
      existing.addEventListener("load", () => {
        window.kakao?.maps.load(() => resolve());
      });
      existing.addEventListener("error", () => {
        reject(new Error("Failed to load Kakao Maps SDK."));
      });
      return;
    }

    const script = document.createElement("script");
    script.async = true;
    script.defer = true;
    script.dataset.kakaoSdk = "true";
    script.src = `https://dapi.kakao.com/v2/maps/sdk.js?autoload=false&appkey=${appKey}`;
    script.onload = () => {
      window.kakao?.maps.load(() => resolve());
    };
    script.onerror = () => {
      reject(new Error("Failed to load Kakao Maps SDK."));
    };

    document.head.appendChild(script);
  });
}

export function KakaoMap({ shops }: { shops: Shop[] }) {
  const appKey = process.env.NEXT_PUBLIC_KAKAO_MAP_APP_KEY;
  const mapRef = useRef<any>(null);
  const markersRef = useRef<any[]>([]);
  const [sdkReady, setSdkReady] = useState(false);
  const [sdkError, setSdkError] = useState<string | null>(null);

  useEffect(() => {
    if (!appKey) {
      return;
    }

    let cancelled = false;

    loadKakaoSdk(appKey)
      .then(() => {
        if (!cancelled) {
          setSdkReady(true);
        }
      })
      .catch((error: Error) => {
        if (!cancelled) {
          setSdkError(error.message);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [appKey]);

  useEffect(() => {
    if (!sdkReady || !window.kakao?.maps) {
      return;
    }

    const container = document.getElementById(MAP_CONTAINER_ID);

    if (!container) {
      return;
    }

    const validShops = shops.filter(
      (shop) => typeof shop.lat === "number" && typeof shop.lng === "number"
    );

    if (!mapRef.current) {
      mapRef.current = new window.kakao.maps.Map(container, {
        center: new window.kakao.maps.LatLng(DEFAULT_CENTER.lat, DEFAULT_CENTER.lng),
        level: 13
      });
    }

    for (const marker of markersRef.current) {
      marker.setMap(null);
    }

    markersRef.current = [];

    if (validShops.length === 0) {
      mapRef.current.setCenter(
        new window.kakao.maps.LatLng(DEFAULT_CENTER.lat, DEFAULT_CENTER.lng)
      );
      return;
    }

    const bounds = new window.kakao.maps.LatLngBounds();

    for (const shop of validShops) {
      const position = new window.kakao.maps.LatLng(shop.lat!, shop.lng!);
      const marker = new window.kakao.maps.Marker({ position });
      const infoWindow = new window.kakao.maps.InfoWindow({
        content: buildInfoWindow(shop)
      });

      marker.setMap(mapRef.current);
      window.kakao.maps.event.addListener(marker, "click", () => {
        infoWindow.open(mapRef.current, marker);
      });
      bounds.extend(position);
      markersRef.current.push(marker);
    }

    mapRef.current.setBounds(bounds);
  }, [sdkReady, shops]);

  if (!appKey) {
    return (
      <div className="map-empty-state">
        <p>카카오 지도 키가 아직 설정되지 않았습니다.</p>
        <p>
          <code>apps/web/.env.local</code>에{" "}
          <code>NEXT_PUBLIC_KAKAO_MAP_APP_KEY</code>를 넣으면 실제 지도가 렌더링됩니다.
        </p>
      </div>
    );
  }

  if (sdkError) {
    return <div className="map-empty-state">{sdkError}</div>;
  }

  return <div id={MAP_CONTAINER_ID} className="map-canvas" />;
}
