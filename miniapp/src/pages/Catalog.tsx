import { useEffect, useState } from "react"
import { fetchCategories, fetchProducts } from "../api"
import { CategoryTabs } from "../components/CategoryTabs"
import { ProductCard } from "../components/ProductCard"
import { useI18n } from "../i18n"
import { CATEGORIES } from "../types"
import type { Product } from "../types"
import { getStartParam } from "../telegram"

export function Catalog() {
  const { t } = useI18n()
  const [category, setCategory] = useState<string | null>(null)
  const [categories, setCategories] = useState<string[]>([...CATEGORIES])
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [query, setQuery] = useState("")
  const popular = getStartParam() === "popular"

  useEffect(() => {
    let active = true
    fetchCategories()
      .then((data) => {
        if (active && data.length) setCategories(data)
      })
      .catch(() => {
        /* оставляем дефолтные категории */
      })
    return () => {
      active = false
    }
  }, [])

  useEffect(() => {
    let active = true
    setLoading(true)
    setError(null)
    fetchProducts(category ?? undefined)
      .then((data) => {
        if (active) setProducts(popular ? [...data].sort((a, b) => b.id - a.id).slice(0, 12) : data)
      })
      .catch((e: Error) => {
        if (active) setError(e.message)
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => {
      active = false
    }
  }, [category, popular])

  const visible = products.filter((p) => p.title.toLowerCase().includes(query.toLowerCase()) || p.description.toLowerCase().includes(query.toLowerCase()))
  return (
    <div className="page">
      <section className="hero">
        <p className="eyebrow">MG MARKET</p>
        <h1 className="page__title">{t("shop_title")}</h1>
        <p className="hero__subtitle">{t("shop_subtitle")}</p>
      </section>
      <label className="search"><span>⌕</span><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder={t("search")} /></label>
      <CategoryTabs
        categories={categories}
        active={category}
        onChange={setCategory}
      />
      {loading && <p className="hint">{t("loading")}</p>}
      {error && <p className="error">{error}</p>}
      {!loading && !error && visible.length === 0 && (
        <div className="empty"><div className="empty__icon">⌕</div><strong>{query ? t("search_empty") : t("nothing_found")}</strong><p>{query ? t("search_empty_desc") : ""}</p></div>
      )}
      <div className="grid">
        {visible.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </div>
  )
}
