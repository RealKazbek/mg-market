from app import db, seed


def test_seed_if_empty_populates_once_and_preserves_existing_products(tmp_path, monkeypatch):
    database_path = tmp_path / "shop.sqlite3"
    monkeypatch.setattr(
        db,
        "get_settings",
        lambda: type("Settings", (), {"database_path": str(database_path)})(),
    )

    db.init_db()
    assert seed.seed_if_empty() is True
    with db.db_session() as conn:
        count = conn.execute("SELECT COUNT(*) AS c FROM products").fetchone()["c"]
        conn.execute(
            "UPDATE products SET title = ? WHERE id = 1", ("Admin custom product",)
        )
    assert count == len(seed.P)

    assert seed.seed_if_empty() is False
    with db.db_session() as conn:
        row = conn.execute("SELECT title FROM products WHERE id = 1").fetchone()
        assert row["title"] == "Admin custom product"
