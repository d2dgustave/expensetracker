DROP TABLE IF EXISTS expense_category;
DROP TABLE IF EXISTS expense;

CREATE TABLE expense_category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE expense (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    description TEXT NOT NULL,
    vendor TEXT,
    category_id INTEGER NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (category_id) REFERENCES expense_category (id)
);
