import { useId } from 'react';

/** An animated, code-native archivist: one floating group keeps figure and halos aligned. */
export function Keeper({ network, onToggle, label }: { network: boolean; onToggle: () => void; label: string }) {
  const id = useId().replace(/:/g, '');
  return <button className={`room-keeper${network ? ' is-network' : ''}`} onClick={onToggle} aria-label={label} title={label} aria-pressed={network}>
    <span className="keeper-body"><span className="keeper-aura" /><span className="keeper-orbit orbit-one" /><span className="keeper-orbit orbit-two" />
    <svg className="keeper-figure" viewBox="0 0 240 280" fill="none" aria-hidden="true">
      <defs>
        <linearGradient id={`${id}-metal`} x1="60" y1="70" x2="182" y2="200" gradientUnits="userSpaceOnUse"><stop stopColor="#6a807c"/><stop offset=".3" stopColor="#233d3b"/><stop offset=".65" stopColor="#0a1a21"/><stop offset="1" stopColor="#55726a"/></linearGradient>
        <linearGradient id={`${id}-hood`} x1="70" y1="90" x2="170" y2="190" gradientUnits="userSpaceOnUse"><stop stopColor="#92a99b"/><stop offset=".34" stopColor="#273b3c"/><stop offset=".8" stopColor="#0a121a"/><stop offset="1" stopColor="#71897e"/></linearGradient>
        <linearGradient id={`${id}-visor`} x1="95" y1="67" x2="155" y2="115" gradientUnits="userSpaceOnUse"><stop stopColor="#102b2c"/><stop offset=".5" stopColor="#041113"/><stop offset="1" stopColor="#578b77"/></linearGradient>
        <radialGradient id={`${id}-light`}><stop stopColor="#d9f6b5" stopOpacity=".8"/><stop offset="1" stopColor="#94ddb7" stopOpacity="0"/></radialGradient>
      </defs>
      <ellipse cx="120" cy="257" rx="88" ry="13" fill={`url(#${id}-light)`}/>
      <ellipse cx="120" cy="250" rx="68" ry="11" stroke="#7aaf97" strokeOpacity=".5"/>
      <path className="keeper-mantle" d="M101 128 65 142 47 194 73 219 99 246 143 246 164 224 193 197 174 148 141 128Z" fill={`url(#${id}-metal)`} stroke="#637d70" strokeWidth=".8"/>
      <path d="m98 135 22 15 23-15 24 15-17 94H92l-17-94Z" fill="#101f25" stroke="#415a53"/>
      <path d="m92 164 28 19 29-19-9 64h-39Z" fill="#17312f"/>
      <path d="m120 150-1 95m-43-96 27 41m62-40-27 41" stroke="#9bb693" strokeOpacity=".5"/>
      <path className="keeper-arm" d="m66 147-20 51 14 18 32-31-11-8-16 19 16-43Z" fill={`url(#${id}-metal)`} stroke="#627b70"/>
      <g className="keeper-hand"><path d="m170 147 25 44-4 19-17-4-20-32 11-13 16 25-11-37Z" fill={`url(#${id}-metal)`} stroke="#7c9883"/><path d="m178 184 5-18 5 2 3 14 10-4 5 7-12 10-15-2Z" fill="#839983"/><circle cx="191" cy="155" r="25" fill={`url(#${id}-light)`}/><path d="m191 133 11 14-11 16-11-16Z" fill="#afdfa2" fillOpacity=".4" stroke="#d9f6b5"/><path d="m191 133-1 30m-10-16h22" stroke="#e1fac2" strokeOpacity=".5"/></g>
      <g className="keeper-head"><path d="m88 118-8-28 8-38 21-19h23l23 19 9 36-12 35-16 18h-30Z" fill={`url(#${id}-hood)`} stroke="#8b9d85" strokeWidth=".8"/>
        <path d="m91 76 16-23h27l18 25-7 35-24 18-25-18Z" fill={`url(#${id}-visor)`} stroke="#9bb99a" strokeOpacity=".65"/>
        <path d="m91 76 29 7 32-5-11 26-20 9-22-12Z" fill="#071417"/>
        <path className="keeper-eyes" d="m100 89 13 4m16 0 13-5" stroke="#defdb4" strokeWidth="2.5" strokeLinecap="round"/>
        <path d="m117 109 5 2 6-3m-6 4v10m-22-50 7-17m35 20-9-22" stroke="#89b39b" strokeOpacity=".5"/>
        <path d="m120 34 1 18m-32 66 14 6m47-7-13 8" stroke="#c4d9b2" strokeWidth="1.2"/>
      </g>
      <circle cx="120" cy="172" r="10" fill={`url(#${id}-light)`}/><path d="m120 165 4 7-4 7-4-7Z" stroke="#c8e9aa"/>
      <path d="M57 246h14m98 0h14M120 21v-8m-73 95-6-3m151 0 6-3" stroke="#a4c891" strokeOpacity=".6"/>
    </svg></span>
    <span className="keeper-plinth"><i /><span>NaCl</span><i /></span>
    <span className="keeper-name">THE ARCHIVIST</span>
    <span className="keeper-switch-label">{label} <span aria-hidden="true">↗</span></span>
  </button>;
}
