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
    user_review TEXT[],
    PRIMARY KEY(user_id)
);

CREATE TABLE IF NOT EXISTS review 
(
    review_id SERIAL NOT NULL,
  	review_author text,
    review text,
    PRIMARY KEY(review_id)
);

CREATE EXTENSION IF NOT EXISTS fuzzystrmatch
