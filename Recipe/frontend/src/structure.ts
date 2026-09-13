import type { FactorCard, StructureScope, StructureType } from './types';

export const TYPE_LABEL: Record<StructureType, string> = {
  directional: '方向性',
  conditional: '条件性',
  shape: '形状性',
  directional_conditional: '方向性×条件性',
};

export const TYPE_SHORT: Record<StructureType, string> = {
  directional: '方向',
  conditional: '条件',
  shape: '形状',
  directional_conditional: '方向×条件',
};

export const SCOPE_LABEL: Record<StructureScope, string> = {
  single: '单标的',
  cross_section: '截面',
  multi_leg: '多腿',
};

export function shortName(card: FactorCard) {
  return card.name.split(/\s*（/)[0];
}
