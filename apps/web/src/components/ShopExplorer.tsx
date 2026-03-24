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
  const hasDataset = dataset.count > 0;

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

  const emptyMessage = hasDataset
    ? "조건에 맞는 안마원이 없습니다. 검색어나 지역을 다시 선택해보세요."
    : "아직 공개용 데이터가 준비 중입니다. 수집이 완료되면 이곳에 안마원 목록이 표시됩니다.";

  return (
    <div className="explorer-shell">
      <section className="hero-card">
        <div>
          <p className="eyebrow">National Certified Massage Map</p>
          <h1>전국 국가공인 안마원을 지역과 지도에서 찾아보세요</h1>
          <p className="hero-copy">
            국가 공인 안마원 목록을 지역별로 찾고, 지도에서 위치를 확인하고, 상세 페이지로
            바로 이동할 수 있도록 한곳에 모았습니다.
          </p>
          <div className="hero-badges">
            <span>지역별 검색</span>
            <span>지도 탐색</span>
            <span>상세 페이지 연결</span>
          </div>
          <p className="hero-status">
            {hasDataset
              ? "현재 공개된 데이터 기준으로 검색과 지도 탐색을 바로 이용할 수 있습니다."
              : "현재는 서비스 화면과 탐색 흐름을 먼저 준비 중이며, 데이터가 들어오면 검색 결과가 함께 표시됩니다."}
          </p>
        </div>
        <dl className="hero-stats">
          <div>
            <dt>등록 안마원</dt>
            <dd>{dataset.count}</dd>
          </div>
          <div>
            <dt>지도 표시 가능</dt>
            <dd>{geocodedCount}</dd>
          </div>
          <div>
            <dt>최근 데이터 갱신</dt>
            <dd>{formatDate(dataset.generatedAt)}</dd>
          </div>
        </dl>
      </section>

      <section className="service-grid">
        <article className="service-card">
          <h2>이용 방법</h2>
          <p>상호명, 주소, 전화번호로 검색하고 원하는 지역을 선택해 안마원을 빠르게 좁혀보세요.</p>
        </article>
        <article className="service-card">
          <h2>확인할 수 있는 정보</h2>
          <p>주소, 전화번호, 지역 정보와 함께 지도 표시 여부를 확인하고 상세 페이지로 이동할 수 있습니다.</p>
        </article>
        <article className="service-card">
          <h2>데이터 기준</h2>
          <p>국가 공인 안마원 목록을 바탕으로 정리되며, 수집 시점에 따라 최신 갱신 시각이 함께 표시됩니다.</p>
        </article>
      </section>

      <section className="control-grid">
        <label className="control-card">
          <span>안마원 이름 / 주소 검색</span>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="예: 서울, 경기, 안마원 이름"
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
            <p>검색 결과 {filteredShops.length}곳</p>
          </div>
          <KakaoMap shops={filteredShops} />
        </div>

        <div className="panel">
          <div className="panel-header">
            <h2>목록</h2>
            <p>전화번호와 상세 페이지를 함께 확인할 수 있습니다.</p>
          </div>
          <div className="shop-list">
            {filteredShops.length === 0 ? (
              <div className="empty-list">{emptyMessage}</div>
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
