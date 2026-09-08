import { useEffect, useState } from 'react';
import { api } from '../api';
import { DataTable } from '../components/DataTable';
import { Message } from '../components/Status';
import type { DatasetAvailability, Exchange, Field, Product } from '../types';

export function Atlas() {
  const [exchanges, setExchanges] = useState<Exchange[]>([]); const [products, setProducts] = useState<Product[]>([]); const [selected, setSelected] = useState<Product | null>(null); const [datasets, setDatasets] = useState<DatasetAvailability[]>([]); const [fields, setFields] = useState<Field[]>([]); const [error, setError] = useState('');
  useEffect(() => { Promise.all([api.exchanges(), api.products(), api.fields()]).then(([exchangeData, productData, fieldData]) => { setExchanges(exchangeData.data); setProducts(productData.data); setFields(fieldData.data); }).catch((reason) => setError(reason.message)); }, []);
  async function selectProduct(product: Product) { setSelected(product); try { setDatasets((await api.availability(product.product_id)).data.datasets); } catch (reason) { setError(reason instanceof Error ? reason.message : String(reason)); } }
  return <div className="page"><div className="page-heading"><div><div className="eyebrow">DATA ATLAS</div><h1>数据目录与字段语义</h1><p>通过 Catalog 查看交易所、品种、数据集和字段，不遍历物理行情文件。</p></div></div>{error && <Message kind="error">{error}</Message>}<section className="metric-grid"><div className="metric"><strong>{exchanges.length}</strong><span>交易所</span></div><div className="metric"><strong>{products.length}</strong><span>品种</span></div><div className="metric"><strong>{fields.length}</strong><span>已发布字段定义</span></div></section><section className="two-column"><div className="panel"><h2>品种目录</h2><div className="product-list">{products.map((product) => <button className={selected?.product_id === product.product_id ? 'selected' : ''} key={product.product_id} onClick={() => selectProduct(product)}>{product.exchange_id} · {product.product_code}<span>{product.product_name}</span></button>)}</div></div><div className="panel"><h2>{selected ? `${selected.product_code} 数据集` : '选择品种'}</h2><DataTable rows={datasets as unknown as Record<string, unknown>[]} empty="选择品种后显示数据集可用性" /></div></section><section className="panel"><h2>字段语义</h2><DataTable rows={fields as unknown as Record<string, unknown>[]} empty="Catalog 当前没有字段信息" /></section></div>;
}
