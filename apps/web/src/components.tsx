import type { ButtonHTMLAttributes, PropsWithChildren } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Menu, Phone, X } from 'lucide-react';
import { useState } from 'react';

export function Brand() { return <Link className="brand" to="/"><span className="brand-mark">心</span><span>阳光心材料</span></Link>; }
const links = [['产品中心','/products'],['应用方案','/applications'],['材料知识','/knowledge'],['技术资料','/documents'],['关于我们','/about']];
export function Header() { const [open,setOpen]=useState(false); return <header className="site-header"><div className="shell nav"><Brand/><nav className={open?'open':''}>{links.map(([t,h])=><Link onClick={()=>setOpen(false)} key={h} to={h}>{t}</Link>)}<Link className="nav-cta" to="/inquiry">咨询选材 <ArrowRight size={16}/></Link></nav><button className="menu" onClick={()=>setOpen(!open)} aria-label="切换导航">{open?<X/>:<Menu/>}</button></div></header> }
export function Footer() { return <footer><div className="shell footer-grid"><div><Brand/><p>面向中国制造企业，提供产品资料、材料选型、样品测试与应用支持。</p></div><div><strong>快速入口</strong><Link to="/products">产品中心</Link><Link to="/applications">应用方案</Link><Link to="/knowledge">材料知识</Link></div><div><strong>联系阳光心材料</strong><p><Phone size={14}/> 联系方式待配置</p><Link to="/privacy">隐私政策</Link><Link to="/terms">使用条款</Link><Link to="/disclaimer">资料与商标说明</Link></div></div><div className="shell copyright">© {new Date().getFullYear()} 阳光心材料。公开内容以已审核资料为准。</div></footer> }
export function Button({children,variant='primary',...props}: PropsWithChildren<ButtonHTMLAttributes<HTMLButtonElement>> & {variant?:'primary'|'secondary'}) { return <button {...props} className={`button ${variant} ${props.className||''}`}>{children}</button> }
export function PageIntro({eyebrow,title,children}:{eyebrow:string;title:string;children:React.ReactNode}) { return <section className="page-intro"><div className="shell"><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p className="lede">{children}</p></div></section> }
export function Layout({children}:PropsWithChildren) { return <><Header/><main>{children}</main><Footer/></> }
