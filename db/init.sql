CREATE TABLE IF NOT EXISTS song 
(
    song_id SERIAL NOT NULL,
    name_song text NOT NULL,
	author text,
    review TEXT[],
    PRIMARY KEY(song_id)
);

CREATE TABLE IF NOT EXISTS users
(
    user_id SERIAL NOT NULL,
	user_tg_id text,
    username text NOT NULL,
    user_review INTEGER[],
	user_like INTEGER[],
    PRIMARY KEY(user_id)
);

CREATE EXTENSION IF NOT EXISTS fuzzystrmatch
