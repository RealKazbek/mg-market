"""Idempotent Kazakhstan demo catalogue. Prices are stored in tiyn (KZT)."""
from .db import db_session, init_db

P = [
 ("Наушники Soundcore Q20i","Шумоподавление, 40 часов работы и мягкие амбушюры.",2999000,"electronics-1","Электроника"),
 ("Портативная колонка JBL Go 4","Компактная колонка с насыщенным звуком и защитой IP67.",2499000,"electronics-2","Электроника"),
 ("Умные часы Amazfit Bip 5","Большой экран, мониторинг сна и до 10 дней без зарядки.",3999000,"electronics-3","Электроника"),
 ("Пауэрбанк Baseus 20 000 мА·ч","Быстрая зарядка 20 Вт и два порта для поездок.",1599000,"electronics-4","Электроника"),
 ("Зарядка Anker Nano 20 Вт","Компактный USB-C адаптер для быстрой зарядки дома и в офисе.",899000,"electronics-5","Электроника"),
 ("Клавиатура Keychron K2","Беспроводная механика с тихими переключателями и подсветкой.",4499000,"electronics-6","Электроника"),
 ("Мышь Logitech Pebble 2","Тихая беспроводная мышь для работы и учёбы.",1299000,"electronics-7","Электроника"),
 ("Подставка для ноутбука Ugreen","Алюминиевая подставка освобождает место на столе.",1199000,"electronics-8","Электроника"),
 ("Чехол MagSafe для iPhone","Защита с приятным матовым покрытием и точной посадкой.",699000,"phone-1","Смартфоны и аксессуары"),
 ("Стекло 9H для iPhone","Прозрачное защитное стекло с набором для аккуратной установки.",299000,"phone-2","Смартфоны и аксессуары"),
 ("Автомобильный держатель MagSafe","Надёжно фиксирует телефон на решётке воздуховода.",999000,"phone-3","Смартфоны и аксессуары"),
 ("Беспроводная зарядка 15 Вт","Заряжает смартфон без кабеля — просто положите его сверху.",1299000,"phone-4","Смартфоны и аксессуары"),
 ("Кабель USB-C 2 м","Прочный кабель в тканевой оплётке для дома и автомобиля.",499000,"phone-5","Смартфоны и аксессуары"),
 ("Органайзер для кабелей","Шесть мягких держателей помогают держать рабочее место в порядке.",199000,"phone-6","Смартфоны и аксессуары"),
 ("Настольная лампа Xiaomi","Тёплый свет, три режима яркости и удобное управление.",2199000,"home-1","Для дома"),
 ("Аромадиффузор Airfeel","Тихо ароматизирует комнату и создаёт уютный вечерний свет.",1899000,"home-2","Для дома"),
 ("Мини-увлажнитель воздуха","Компактный увлажнитель для рабочего стола или спальни.",1499000,"home-3","Для дома"),
 ("Умная розетка Wi‑Fi","Управляйте светом и техникой со смартфона.",799000,"home-4","Для дома"),
 ("Набор органайзеров для стола","Лаконичный набор для ручек, заметок и мелочей.",599000,"home-5","Для дома"),
 ("LED-лента 5 м","Мягкая подсветка для комнаты, полки или рабочего места.",899000,"home-6","Для дома"),
 ("Кофейный набор для двоих","Две керамические чашки и подставки в подарочной коробке.",2499000,"home-7","Для дома"),
 ("Автозарядка USB-C 45 Вт","Быстро заряжает два устройства в дороге.",1199000,"auto-1","Авто"),
 ("Пылесос для автомобиля","Беспроводной компактный пылесос для салона и багажника.",3499000,"auto-2","Авто"),
 ("Компрессор для шин","Цифровой манометр и автостоп при нужном давлении.",3299000,"auto-3","Авто"),
 ("Набор для ухода за салоном","Микрофибры, щётки и состав для чистки пластика.",999000,"auto-4","Авто"),
 ("Ароматизатор Cedar Drive","Свежий древесный аромат без резкой сладости.",399000,"auto-5","Авто"),
 ("Складной органайзер в багажник","Три отделения и нескользящее дно.",1499000,"auto-6","Авто"),
 ("Городской рюкзак Urban 20L","Лёгкий рюкзак с отделением для ноутбука 15,6 дюйма.",2999000,"life-1","Lifestyle"),
 ("Термобутылка Steel 500 мл","Держит тепло до 8 часов и не протекает.",1299000,"life-2","Lifestyle"),
 ("Кожаный кошелёк Slim","Тонкий кошелёк для карт, наличных и документов.",2499000,"life-3","Lifestyle"),
 ("Солнцезащитные очки City","Лёгкая оправа и линзы с UV400 для солнечных дней.",1999000,"life-4","Lifestyle"),
 ("Плед Soft Home","Мягкий плед 150×200 см для уютных вечеров.",2799000,"life-5","Lifestyle"),
 ("Набор дорожных органайзеров","Четыре чехла для одежды, обуви и аксессуаров.",1699000,"life-6","Lifestyle"),
 ("Ежедневник Plan 2026","Недатированный планер с плотной бумагой и закладкой.",799000,"life-7","Lifestyle"),
]

# Stable, hand-picked Unsplash asset IDs. Unlike random image services these
# never change between requests; each SKU is mapped to a relevant object.
IMAGE_URLS = {
    "electronics-1":"photo-1505740420928-5e560c06d30e", "electronics-2":"photo-1608043152269-423dbba4e7e1", "electronics-3":"photo-1523275335684-37898b6baf30", "electronics-4":"photo-1625842268584-8f3296236761", "electronics-5":"photo-1583394838336-acd977736f90", "electronics-6":"photo-1511467687858-23d96c32e4ae", "electronics-7":"photo-1527814050087-3793815479db", "electronics-8":"photo-1527443224154-c4a3942d3acf",
    "phone-1":"photo-1511707171634-5f897ff02aa9", "phone-2":"photo-1511707171634-5f897ff02aa9", "phone-3":"photo-1605236453806-6ff36851218e", "phone-4":"photo-1605236453806-6ff36851218e", "phone-5":"photo-1587033411391-5d9e51cce126", "phone-6":"photo-1516321318423-f06f85e504b3",
    "home-1":"photo-1507473885765-e6ed057f782c", "home-2":"photo-1608571423902-eed4a5ad8108", "home-3":"photo-1585771724684-38269d6639fd", "home-4":"photo-1558008258-3256797b43f3", "home-5":"photo-1494438639946-1ebd1d20bf85", "home-6":"photo-1550684848-fac1c5b4e853", "home-7":"photo-1513558161293-cdaf765ed2fd",
    "auto-1":"photo-1619767886558-efdc259cde1a", "auto-2":"photo-1558317374-067fb5f30001", "auto-3":"photo-1544829099-b9a0c07fad1a", "auto-4":"photo-1605559424843-9e4c228bf1c2", "auto-5":"photo-1603006905003-be475563bc59", "auto-6":"photo-1503376780353-7e6692767b70",
    "life-1":"photo-1553062407-98eeb64c6a62", "life-2":"photo-1602143407151-7111542de6e8", "life-3":"photo-1627123424574-724758594e93", "life-4":"photo-1511499767150-a48a237f0083", "life-5":"photo-1456324504439-367cee3b3c32", "life-6":"photo-1512418490979-92798cec1380", "life-7":"photo-1456324504439-367cee3b3c32",
}

def _seed_into(conn) -> None:
    for title, desc, price, image, category in P:
        # Stable image seeds keep cards varied without bundling large assets.
        url = f"https://images.unsplash.com/{IMAGE_URLS[image]}?auto=format&fit=crop&w=700&q=85"
        conn.execute(
            "INSERT INTO products (title,description,price_kopecks,photo_url,category) "
            "VALUES (?,?,?,?,?)",
            (title, desc, price, url, category),
        )
        conn.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))
    print(f"Каталог добавлен: {len(P)} товаров")


def seed() -> None:
    """Reset the product catalogue to the bundled demo catalogue (manual use)."""
    init_db()
    with db_session() as conn:
        # Preserve the original explicit seed command's behaviour for local use.
        for i, (title, desc, price, image, category) in enumerate(P, 1):
            url = f"https://images.unsplash.com/{IMAGE_URLS[image]}?auto=format&fit=crop&w=700&q=85"
            row = conn.execute("SELECT id FROM products ORDER BY id LIMIT 1 OFFSET ?", (i - 1,)).fetchone()
            if row:
                conn.execute("UPDATE products SET title=?, description=?, price_kopecks=?, photo_url=?, category=?, is_active=1 WHERE id=?", (title, desc, price, url, category, row["id"]))
            else:
                conn.execute("INSERT INTO products (title,description,price_kopecks,photo_url,category) VALUES (?,?,?,?,?)", (title, desc, price, url, category))
            conn.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))
        keep = tuple(sorted({row[4] for row in P}))
        placeholders = ",".join("?" for _ in keep)
        conn.execute(f"DELETE FROM categories WHERE name NOT IN ({placeholders}) AND name NOT IN (SELECT DISTINCT category FROM products)", keep)
        print(f"Каталог обновлён: {len(P)} товаров")


def seed_if_empty() -> bool:
    """Add the default catalogue only when products is empty.

    The write lock makes the check-and-seed operation safe if startup overlaps.
    """
    with db_session() as conn:
        conn.execute("BEGIN IMMEDIATE")
        if conn.execute("SELECT 1 FROM products LIMIT 1").fetchone():
            return False
        _seed_into(conn)
        return True

if __name__ == "__main__":
    seed()
