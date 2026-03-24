import { ShopExplorer } from "@/components/ShopExplorer";
import { getDataset } from "@/lib/dataset";

export default async function HomePage() {
  const dataset = await getDataset();

  return (
    <main className="page-shell">
      <ShopExplorer dataset={dataset} />
    </main>
  );
}
