DROP TABLE IF EXISTS expense_category;

CREATE TABLE expense_category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT
);
