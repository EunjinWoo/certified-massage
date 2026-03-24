export type GeocodeStatus = "pending" | "success" | "failed" | "skipped";

export interface Shop {
  shopId: string;
  name: string;
  addressRaw: string;
  addressNormalized: string;
  phone: string;
  areaCode: string;
  sourceListPage: number | null;
  detailUrl: string;
  lat: number | null;
  lng: number | null;
  geocodeStatus: GeocodeStatus;
  sourceFetchedAt: string;
}

export interface ShopDataset {
  generatedAt: string | null;
  count: number;
  shops: Shop[];
}
