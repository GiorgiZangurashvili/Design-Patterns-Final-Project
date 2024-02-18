PRAGMA foreign_keys = ON;
drop table if exists users;
create table users(
    id INTEGER PRIMARY KEY,
    mail TEXT,
    first_wallet_id INTEGER DEFAULT 0,
    second_wallet_id INTEGER DEFAULT 0,
    third_wallet_id INTEGER DEFAULT 0
);

drop table if exists wallets;
create table wallets(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    balance REAL DEFAULT 1
);

drop table if exists transactions;
create table transactions(
    id INTEGER PRIMARY KEY,
    from_wallet_id INTEGER,
    to_wallet_id INTEGER,
    amount_transferred REAL DEFAULT 0.0,
    lost_amount REAL DEFAULT 0.0
);
