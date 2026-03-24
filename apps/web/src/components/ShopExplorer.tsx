"use client";

import { useState } from "react";

import { KakaoMap } from "@/components/KakaoMap";
import { getAreaFilterLabel, getAreaLabel } from "@/lib/regions";
import type { ShopDataset } from "@/lib/types";

function formatDate(value: string | null): string {
  if (!value) {
    return "아직 생성되지 않음";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("ko-KR", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(date);
}

export function ShopExplorer({ dataset }: { dataset: ShopDataset }) {
  const [query, setQuery] = useState("");
  const [areaCode, setAreaCode] = useState("all");

  const areas = Array.from(
    new Set(dataset.shops.map((shop) => shop.areaCode).filter(Boolean))
  ).sort((left, right) => left.localeCompare(right));

  const filteredShops = dataset.shops.filter((shop) => {
    const matchesArea = areaCode === "all" || shop.areaCode === areaCode;
    const keyword = query.trim().toLowerCase();

    if (!matchesArea) {
      return false;
    }

    if (!keyword) {
      return true;
    }

    return [
      shop.name,
      shop.addressNormalized,
      shop.addressRaw,
      shop.phone,
      shop.shopId
    ]
      .join(" ")
      .toLowerCase()
      .includes(keyword);
  });

  const geocodedCount = dataset.shops.filter(
    (shop) => typeof shop.lat === "number" && typeof shop.lng === "number"
  ).length;

  return (
    <div className="explorer-shell">
      <section className="hero-card">
        <div>
          <p className="eyebrow">Certified Massage Map</p>
          <h1>국가 공인 안마원 데이터를 수집하고 지도에 올리는 작업실</h1>
          <p className="hero-copy">
            크롤러가 생성한 <code>shops.geo.json</code>을 읽어 목록과 지도를 함께 보여줍니다.
            현재는 MVP 스캐폴딩이 준비되어 있고, 실제 데이터가 쌓이면 검색과 필터가 바로 작동합니다.
          </p>
        </div>
        <dl className="hero-stats">
          <div>
            <dt>전체 안마원</dt>
            <dd>{dataset.count}</dd>
          </div>
          <div>
            <dt>좌표 확보</dt>
            <dd>{geocodedCount}</dd>
          </div>
          <div>
            <dt>데이터 생성</dt>
            <dd>{formatDate(dataset.generatedAt)}</dd>
          </div>
        </dl>
      </section>

      <section className="control-grid">
        <label className="control-card">
          <span>상호명 / 주소 검색</span>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="예: 서울, 031-0193, 안마원 이름"
          />
        </label>

        <label className="control-card">
          <span>지역</span>
          <select
            value={areaCode}
            onChange={(event) => setAreaCode(event.target.value)}
          >
            <option value="all">전체</option>
            {areas.map((value) => (
              <option key={value} value={value}>
                {getAreaFilterLabel(value)}
              </option>
            ))}
          </select>
        </label>
      </section>

      <section className="content-grid">
        <div className="panel">
          <div className="panel-header">
            <h2>지도</h2>
            <p>{filteredShops.length}개 결과</p>
          </div>
          <KakaoMap shops={filteredShops} />
        </div>

        <div className="panel">
          <div className="panel-header">
            <h2>목록</h2>
            <p>
              좌표 없는 항목도 목록에서는 확인할 수 있습니다.
            </p>
          </div>
          <div className="shop-list">
            {filteredShops.length === 0 ? (
              <div className="empty-list">표시할 안마원이 아직 없습니다.</div>
            ) : null}

            {filteredShops.map((shop) => (
              <article key={shop.shopId} className="shop-card">
                <div className="shop-card-top">
                  <div>
                    <h3>{shop.name || "이름 미상"}</h3>
                    <p>{shop.addressNormalized || shop.addressRaw || "주소 미상"}</p>
                  </div>
                  <span className="shop-chip">{getAreaLabel(shop.areaCode)}</span>
                </div>
                <dl className="shop-meta">
                  <div>
                    <dt>전화</dt>
                    <dd>{shop.phone || "없음"}</dd>
                  </div>
                  <div>
                    <dt>shopId</dt>
                    <dd>{shop.shopId}</dd>
                  </div>
                  <div>
                    <dt>지오코딩</dt>
                    <dd>{shop.geocodeStatus}</dd>
                  </div>
                </dl>
                <a
                  href={shop.detailUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="detail-link"
                >
                  상세 페이지 열기
                </a>
              </article>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
