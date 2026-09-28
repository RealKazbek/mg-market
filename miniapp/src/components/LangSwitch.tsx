import { useI18n } from "../i18n"

export function LangSwitch() {
  const { lang, setLang } = useI18n()
  return (
    <div className="lang-switch">
      <button
        type="button"
        className={`lang-switch__btn ${lang === "kk" ? "is-active" : ""}`}
        onClick={() => setLang("kk")}
      >
        🇰🇿
      </button>
      <button
        type="button"
        className={`lang-switch__btn ${lang === "ru" ? "is-active" : ""}`}
        onClick={() => setLang("ru")}
      >
        🇷🇺
      </button>
      <button
        type="button"
        className={`lang-switch__btn ${lang === "en" ? "is-active" : ""}`}
        onClick={() => setLang("en")}
      >
        🇬🇧
      </button>
    </div>
  )
}
