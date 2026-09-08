type Props = { rows: Record<string, unknown>[]; empty?: string };

export function DataTable({ rows, empty = '暂无数据' }: Props) {
  if (!rows.length) return <div className="empty-state">{empty}</div>;
  const columns = Object.keys(rows[0]);
  return <div className="table-scroll"><table><thead><tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr></thead><tbody>{rows.map((row, index) => <tr key={index}>{columns.map((column) => <td key={column}>{String(row[column] ?? '—')}</td>)}</tr>)}</tbody></table></div>;
}
