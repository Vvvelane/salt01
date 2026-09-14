import type { FactorCard, StructureScope, StructureType } from './types';

export const TYPE_LABEL: Record<StructureType, string> = {
  directional: '方向信号', conditional: '条件强度', shape: '分布形态', directional_conditional: '方向 × 条件',
};
export const SCOPE_LABEL: Record<StructureScope, string> = {
  single: '单合约', cross_section: '横截面组合', multi_leg: '多合约价差',
};
export function shortName(card: FactorCard, language = 'normal') {
  if (language === 'en') return card.name.match(/（([^（）]*[A-Za-z][^（）]*)）\s*$/)?.[1] ?? card.factor_id;
  return card.name.split(/\s*（/)[0];
}
