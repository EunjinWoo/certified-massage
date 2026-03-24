import { readFile } from "node:fs/promises";
import path from "node:path";

import type { ShopDataset } from "@/lib/types";

const EMPTY_DATASET: ShopDataset = {
  generatedAt: null,
  count: 0,
  shops: []
};

const DATASET_PATH = path.join(
  process.cwd(),
  "..",
  "..",
  "data",
  "processed",
  "shops.geo.json"
);

export async function getDataset(): Promise<ShopDataset> {
  try {
    const payload = await readFile(DATASET_PATH, "utf-8");
    const parsed = JSON.parse(payload) as Partial<ShopDataset>;

    if (!parsed || !Array.isArray(parsed.shops)) {
      return EMPTY_DATASET;
    }

    return {
      generatedAt: parsed.generatedAt ?? null,
      count: parsed.count ?? parsed.shops.length,
      shops: parsed.shops
    };
  } catch {
    return EMPTY_DATASET;
  }
}
