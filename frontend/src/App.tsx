import { useCallback, useEffect, useMemo, useState, type FormEvent, type ReactNode } from 'react'
import { Activity, ArrowLeftRight, ArrowUpRight, Bell, Boxes, ChartNoAxesCombined, Check, ChevronDown, CircleHelp, LayoutDashboard, LogOut, Menu, Package, Plus, Search, Settings, ShieldCheck, Shirt, Sparkles, X } from 'lucide-react'
import { api, ApiError, type Product, type User, type VariantInventory } from './api'

type Page = 'overview' | 'products' | 'movements' | 'reports' | 'settings'
const TOKEN_KEY = 'modastock_access_token'
function App() {
  const [token, setToken] = useState<string | null>(() => sessionStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState<User | null>(null)
  const [page, setPage] = useState<Page>('overview')
  const [mobileOpen, setMobileOpen] = useState(false)
  const [authLoading, setAuthLoading] = useState(Boolean(token))
  const [authError, setAuthError] = useState('')
  const [products, setProducts] = useState<Product[]>([])
  const [loadingProducts, setLoadingProducts] = useState(false)
  const [notice, setNotice] = useState('')
  const [search, setSearch] = useState('')
  const [showProductForm, setShowProductForm] = useState(false)
  const [saving, setSaving] = useState(false)
  const [productName, setProductName] = useState('')
  const [productRef, setProductRef] = useState('')
  const [productDescription, setProductDescription] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [registerMode, setRegisterMode] = useState(false)
  const [movementVariant, setMovementVariant] = useState('')
  const [variants, setVariants] = useState<VariantInventory[]>([])
  const [loadingVariants, setLoadingVariants] = useState(false)
  const [movementQty, setMovementQty] = useState('1')
  const [movementType, setMovementType] = useState<'IN' | 'OUT'>('IN')
  const [movementReason, setMovementReason] = useState('Recepción de mercancía')
  const [movementMessage, setMovementMessage] = useState('')
  const [movementSaving, setMovementSaving] = useState(false)

  const logout = useCallback(() => { sessionStorage.removeItem(TOKEN_KEY); setToken(null); setUser(null); setProducts([]) }, [])
  const loadProducts = useCallback(async (accessToken: string) => {
    setLoadingProducts(true)
    try { setProducts(await api.products(accessToken)) }
    catch (error) { if (error instanceof ApiError && error.status === 401) logout(); else setNotice(error instanceof Error ? error.message : 'Error al cargar productos') }
    finally { setLoadingProducts(false) }
  }, [logout])

  useEffect(() => {
    if (!token) { setAuthLoading(false); return }
    let active = true
    api.me(token).then(profile => { if (active) { setUser(profile); void loadProducts(token) } })
      .catch(() => { if (active) logout() }).finally(() => { if (active) setAuthLoading(false) })
    return () => { active = false }
  }, [token, loadProducts, logout])

  useEffect(() => {
    if (page !== 'movements' || !token) return
    let active = true
    setLoadingVariants(true)
    api.variants(token).then(items => { if (active) { setVariants(items); if (!movementVariant && items.length) setMovementVariant(items[0].id) } })
      .catch(error => { if (active) setMovementMessage(error instanceof Error ? error.message : 'No se pudieron cargar las variantes') })
      .finally(() => { if (active) setLoadingVariants(false) })
    return () => { active = false }
  }, [page, token])
  const filteredProducts = useMemo(() => products.filter(p => `${p.name} ${p.model_reference}`.toLowerCase().includes(search.toLowerCase())), [products, search])
  const doAuth = async (event: FormEvent) => {
    event.preventDefault(); setAuthError(''); setAuthLoading(true)
    try {
      if (registerMode) await api.register(fullName, email, password)
      const result = await api.login(email, password)
      sessionStorage.setItem(TOKEN_KEY, result.access_token); setToken(result.access_token)
      const profile = await api.me(result.access_token); setUser(profile); await loadProducts(result.access_token)
    } catch (error) { setAuthError(error instanceof Error ? error.message : 'No se pudo iniciar sesión') }
    finally { setAuthLoading(false) }
  }
  const saveProduct = async (event: React.FormEvent) => {
    event.preventDefault(); if (!token) return
    setSaving(true); setNotice('')
    try {
      await api.createProduct(token, { name: productName.trim(), model_reference: productRef.trim(), description: productDescription.trim() || undefined })
      setShowProductForm(false); setProductName(''); setProductRef(''); setProductDescription('')
      await loadProducts(token); setNotice('Producto creado correctamente.')
    } catch (error) { setNotice(error instanceof Error ? error.message : 'No se pudo crear el producto') }
    finally { setSaving(false) }
  }
  const saveMovement = async (event: React.FormEvent) => {
    event.preventDefault(); if (!token) return
    setMovementSaving(true); setMovementMessage('')
    try {
      await api.createMovement(token, { variant_id: movementVariant.trim(), movement_type: movementType, quantity: Number(movementQty), reason: movementReason.trim() }, crypto.randomUUID())
      setMovementMessage('Movimiento registrado correctamente.'); await api.variants(token).then(setVariants)
    } catch (error) { setMovementMessage(error instanceof Error ? error.message : 'No se pudo registrar el movimiento') }
    finally { setMovementSaving(false) }
  }

  if (authLoading) return <div className="splash"><div className="brand-mark"><Shirt size={24}/></div><span>Preparando tu espacio de trabajo…</span></div>
  if (!token || !user) return <main className="auth-shell"><section className="auth-visual"><div className="auth-brand"><div className="brand-mark"><Shirt size={23}/></div><span>modastock</span></div><div className="auth-copy"><span className="eyebrow light">CONTROL DE INVENTARIO, CON ESTILO</span><h1>Tu inventario.<br/>En perfecto orden.</h1><p>Una visión clara de cada prenda, cada variante y cada movimiento de tu negocio.</p><div className="auth-stat"><div className="stat-icon"><Boxes size={19}/></div><div><strong>Todo en un solo lugar</strong><small>Productos · Tallas · Colores · Existencias</small></div></div></div><div className="auth-foot">MODASTOCK © 2026</div></section><section className="auth-form-wrap"><form className="auth-card" onSubmit={doAuth}><span className="eyebrow">BIENVENIDO A MODASTOCK</span><h2>{registerMode ? 'Crea tu cuenta' : 'Qué bueno verte de nuevo'}</h2><p className="muted">{registerMode ? 'Registra tu acceso al espacio de inventario.' : 'Ingresa tus datos para continuar.'}</p>{registerMode && <label>Nombre completo<input required minLength={2} value={fullName} onChange={e=>setFullName(e.target.value)} placeholder="Tu nombre"/></label>}<label>Correo electrónico<input required type="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="nombre@tienda.com"/></label><label>Contraseña<input required minLength={registerMode ? 12 : 1} type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder={registerMode ? 'Mínimo 12 caracteres' : 'Tu contraseña'}/></label>{authError && <div className="alert error">{authError}</div>}<button className="btn primary full" disabled={authLoading}>{authLoading ? 'Procesando…' : registerMode ? 'Crear cuenta' : 'Iniciar sesión'}<ArrowUpRight size={17}/></button><button type="button" className="text-button" onClick={()=>{setRegisterMode(!registerMode);setAuthError('')}}>{registerMode ? 'Ya tengo una cuenta · Iniciar sesión' : '¿Primera vez aquí? Crear una cuenta'}</button><div className="secure-note"><ShieldCheck size={15}/> Acceso protegido con autenticación segura</div></form></section></main>

  const nav = [{ id:'overview' as Page, label:'Resumen', icon:LayoutDashboard },{ id:'products' as Page,label:'Productos',icon:Package },{ id:'movements' as Page,label:'Movimientos',icon:ArrowLeftRight },{ id:'reports' as Page,label:'Reportes',icon:ChartNoAxesCombined }]
  const title = ({overview:'Resumen general',products:'Productos',movements:'Movimientos de inventario',reports:'Reportes',settings:'Configuración'} as Record<Page,string>)[page]
  return <div className="app-shell"><aside className={`sidebar ${mobileOpen?'open':''}`}><div className="side-brand"><div className="brand-mark"><Shirt size={22}/></div><span>modastock</span><button className="icon-button mobile-close" onClick={()=>setMobileOpen(false)}><X size={18}/></button></div><div className="workspace"><div className="workspace-avatar">M</div><div><strong>Mi tienda</strong><small>Plan de inventario</small></div><ChevronDown size={15}/></div><div className="nav-label">MENÚ PRINCIPAL</div><nav>{nav.map(item=><button key={item.id} className={`nav-item ${page===item.id?'active':''}`} onClick={()=>{setPage(item.id);setMobileOpen(false)}}><item.icon size={18}/>{item.label}{item.id==='products' && <span className="nav-count">{products.length}</span>}</button>)}</nav><div className="nav-label secondary-label">PREFERENCIAS</div><button className={`nav-item ${page==='settings'?'active':''}`} onClick={()=>setPage('settings')}><Settings size={18}/>Configuración</button><div className="sidebar-bottom"><div className="help-card"><div className="help-icon"><CircleHelp size={17}/></div><strong>¿Necesitas ayuda?</strong><p>Consulta la guía de uso de ModaStock.</p><button onClick={()=>setNotice('La documentación de usuario estará disponible en la fase de documentación.')}>Ver guía <ArrowUpRight size={13}/></button></div><div className="profile-row"><div className="profile-avatar">{user.full_name.slice(0,1).toUpperCase()}</div><div className="profile-info"><strong>{user.full_name}</strong><small>{user.role}</small></div><button className="icon-button" title="Cerrar sesión" onClick={logout}><LogOut size={17}/></button></div></div></aside><div className="main-area"><header className="topbar"><button className="icon-button menu-toggle" onClick={()=>setMobileOpen(true)}><Menu size={20}/></button><div className="breadcrumb">ModaStock <span>/</span> <strong>{title}</strong></div><div className="top-actions"><div className="status-pill"><span/> Sistema conectado</div><button className="icon-button notification" title="Notificaciones"><Bell size={18}/><i/></button><div className="top-avatar">{user.full_name.slice(0,1).toUpperCase()}</div></div></header><main className="content"><div className="page-heading"><div><span className="eyebrow">PANEL DE CONTROL</span><h1>{title}</h1><p className="muted">{page==='overview'?'Una mirada rápida al estado de tu tienda.':page==='products'?'Administra las prendas y referencias de tu catálogo.':page==='movements'?'Registra entradas y salidas con trazabilidad.':page==='reports'?'Indicadores disponibles a partir de los datos registrados.':'Preferencias de tu espacio de trabajo.'}</p></div>{page==='products' && ['ADMIN','MANAGER'].includes(user.role) && <button className="btn primary" onClick={()=>setShowProductForm(true)}><Plus size={17}/> Nuevo producto</button>}</div>{notice && <div className="alert info">{notice}<button onClick={()=>setNotice('')}><X size={15}/></button></div>}
  {page==='overview' && <><div className="welcome-banner"><div><span className="eyebrow light">TU NEGOCIO, BAJO CONTROL</span><h2>Hola, {user.full_name.split(' ')[0]} <Sparkles size={20}/></h2><p>Todo empieza con un inventario organizado. Aquí tienes el estado actual de tu catálogo.</p><button className="banner-link" onClick={()=>setPage('products')}>Explorar productos <ArrowUpRight size={15}/></button></div><div className="banner-art"><div className="art-circle"><Shirt size={68} strokeWidth={1.1}/></div><div className="art-tag">NEW<br/>COLLECTION</div></div></div><div className="stats-grid"><Stat icon={<Package/>} label="Productos activos" value={String(products.filter(p=>p.is_active).length)} detail="Referencias registradas"/><Stat icon={<Boxes/>} label="Referencias totales" value={String(products.length)} detail="En tu catálogo"/><Stat icon={<Activity/>} label="Movimientos" value="—" detail="Indicador no disponible aún"/><Stat icon={<Bell/>} label="Alertas de stock" value="—" detail="Requiere consulta de variantes"/></div><section className="panel"><div className="panel-head"><div><h3>Productos recientes</h3><p>Últimas referencias agregadas al catálogo</p></div><button className="subtle-link" onClick={()=>setPage('products')}>Ver catálogo <ArrowUpRight size={15}/></button></div><ProductTable products={products.slice(0,5)} loading={loadingProducts}/></section></>}
  {page==='products' && <section className="panel"><div className="panel-head"><div><h3>Catálogo de productos</h3><p>{products.length} referencias registradas</p></div><div className="search-box"><Search size={16}/><input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Buscar producto…"/></div></div><ProductTable products={filteredProducts} loading={loadingProducts}/></section>}
  {page==='movements' && <div className="form-panel"><div className="form-panel-title"><div className="form-icon"><ArrowLeftRight size={20}/></div><div><h3>Registrar movimiento</h3><p>Registra una entrada o salida de mercancía para una variante existente.</p></div></div><form className="stack-form" onSubmit={saveMovement}><label>Variante de producto<select required value={movementVariant} onChange={e=>setMovementVariant(e.target.value)} disabled={loadingVariants || variants.length===0}><option value="">{loadingVariants ? "Cargando variantes…" : "Selecciona una variante"}</option>{variants.map(v=><option key={v.id} value={v.id}>{v.sku} · {v.product_name} · {v.size_name}/{v.color_name} · Stock: {v.quantity}</option>)}</select></label>{variants.length===0 && !loadingVariants && <div className="alert info">No hay variantes activas. Crea una variante desde el catálogo para poder registrar movimientos.</div>}<div className="two-fields"><label>Tipo de movimiento<select value={movementType} onChange={e=>setMovementType(e.target.value as 'IN'|'OUT')}><option value="IN">Entrada de mercancía</option><option value="OUT">Salida de mercancía</option></select></label><label>Cantidad<input type="number" min="1" required value={movementQty} onChange={e=>setMovementQty(e.target.value)}/></label></div><label>Motivo<input required value={movementReason} onChange={e=>setMovementReason(e.target.value)} maxLength={250}/></label>{movementMessage && <div className={`alert ${movementMessage.includes('correctamente')?'success':'error'}`}>{movementMessage}</div>}<button className="btn primary" disabled={movementSaving || !movementVariant || loadingVariants}>{movementSaving?'Guardando…':'Confirmar movimiento'}<ArrowUpRight size={16}/></button></form><p className="form-hint">La API valida permisos, existencias e idempotencia. La variante debe existir previamente.</p></div>}
  {page==='reports' && <div className="empty-state"><div className="empty-icon"><ChartNoAxesCombined size={26}/></div><h3>Reportes en preparación</h3><p>Los indicadores se habilitarán cuando estén disponibles los endpoints de análisis y agregación de inventario.</p></div>}
  {page==='settings' && <section className="panel settings-panel"><div className="panel-head"><div><h3>Cuenta y seguridad</h3><p>Información de tu sesión actual</p></div><ShieldCheck size={21}/></div><div className="setting-line"><span>Nombre</span><strong>{user.full_name}</strong></div><div className="setting-line"><span>Correo</span><strong>{user.email}</strong></div><div className="setting-line"><span>Rol</span><strong className="role-tag">{user.role}</strong></div><div className="setting-line"><span>Estado</span><strong className="active-tag">Activo</strong></div><button className="btn outline" onClick={logout}><LogOut size={16}/> Cerrar sesión</button></section>}
  <footer className="footer"><span>© 2026 ModaStock</span><span>Hecho para gestionar mejor.</span></footer></main></div>{showProductForm && <div className="modal-backdrop" onMouseDown={e=>{if(e.target===e.currentTarget)setShowProductForm(false)}}><form className="modal" onSubmit={saveProduct}><div className="modal-head"><div><span className="eyebrow">CATÁLOGO</span><h2>Nuevo producto</h2></div><button type="button" className="icon-button" onClick={()=>setShowProductForm(false)}><X size={19}/></button></div><label>Nombre del producto<input required maxLength={150} value={productName} onChange={e=>setProductName(e.target.value)} placeholder="Ej. Camiseta básica oversize"/></label><label>Referencia del modelo<input required maxLength={80} value={productRef} onChange={e=>setProductRef(e.target.value)} placeholder="Ej. CAM-OV-001"/></label><label>Descripción <span className="optional">Opcional</span><textarea rows={3} value={productDescription} onChange={e=>setProductDescription(e.target.value)} placeholder="Describe brevemente el producto…"/></label><div className="modal-actions"><button type="button" className="btn outline" onClick={()=>setShowProductForm(false)}>Cancelar</button><button className="btn primary" disabled={saving}>{saving?'Guardando…':'Guardar producto'}<Check size={16}/></button></div></form></div>}</div>
}
function Stat({icon,label,value,detail}:{icon:ReactNode;label:string;value:string;detail:string}) { return <div className="stat-card"><div className="stat-top"><span>{label}</span><i>{icon}</i></div><strong>{value}</strong><small>{detail}</small></div> }
function ProductTable({products,loading}:{products:Product[];loading:boolean}) { return <div className="table-wrap"><table><thead><tr><th>PRODUCTO</th><th>REFERENCIA</th><th>ESTADO</th><th>FECHA DE REGISTRO</th></tr></thead><tbody>{loading?<tr><td colSpan={4} className="table-empty">Cargando catálogo…</td></tr>:products.length===0?<tr><td colSpan={4} className="table-empty">No hay productos para mostrar.</td></tr>:products.map(p=><tr key={p.id}><td><div className="product-cell"><div className="product-thumb"><Shirt size={18}/></div><strong>{p.name}</strong></div></td><td><span className="reference">{p.model_reference}</span></td><td><span className={`status-tag ${p.is_active?'active':'inactive'}`}><i/>{p.is_active?'Activo':'Inactivo'}</span></td><td>{new Date(p.created_at).toLocaleDateString('es-CO',{day:'2-digit',month:'short',year:'numeric'})}</td></tr>)}</tbody></table></div> }
export default App
