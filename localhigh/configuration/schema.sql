CREATE TABLE IF NOT EXISTS users (
    id  str unique not null,
    email str unique not null,
    name str not null,
);