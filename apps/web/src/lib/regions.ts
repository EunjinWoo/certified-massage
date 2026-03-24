const AREA_CODE_LABELS: Record<string, string> = {
  "02": "서울",
  "031": "경기",
  "032": "인천",
  "033": "강원",
  "041": "충남",
  "042": "대전",
  "043": "충북",
  "051": "부산",
  "052": "울산",
  "053": "대구",
  "054": "경북",
  "055": "경남",
  "061": "전남",
  "062": "광주",
  "063": "전북",
  "064": "제주"
};

export function getAreaLabel(areaCode: string): string {
  const normalized = areaCode.trim();

  if (!normalized) {
    return "미분류";
  }

  return AREA_CODE_LABELS[normalized] ?? normalized;
}

export function getAreaFilterLabel(areaCode: string): string {
  const normalized = areaCode.trim();

  if (!normalized) {
    return "미분류";
  }

  const areaLabel = getAreaLabel(normalized);

  if (areaLabel === normalized) {
    return normalized;
  }

  return `${areaLabel} (${normalized})`;
}
