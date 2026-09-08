import { Status } from '../components/Status';

export function Research() {
  return <div className="page"><div className="page-heading"><div><div className="eyebrow">RESEARCH AUDIT</div><h1>研究结果</h1><p>Recipe 只展示已注册的研究产物，不在前端计算因子或回测。</p></div><Status>占位</Status></div><section className="panel empty-state"><h2>暂无研究输出</h2><p>Research 保持接口和展示位置，但当前没有注册 factorlab manifest。</p><p>后续只需要接入经过验证的 run manifest、指标、交易和曲线文件。</p></section></div>;
}
