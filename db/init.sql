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

INSERT INTO song (name_song, author, review) VALUES
('Bohemian Rhapsody', 'Queen', '{"Amazing classic!", "Timeless rock opera."}'),
('Imagine', 'John Lennon', '{"Peaceful and hopeful.", "Universal message."}'),
('Hotel California', 'Eagles', '{"Mysterious and iconic.", "Great guitar solo."}'),
('Smells Like Teen Spirit', 'Nirvana', '{"Grunge anthem.", "Changed music in the 90s."}')
ON CONFLICT DO NOTHING;

INSERT INTO users (user_id, username, user_tg_id) 
VALUES (999, 'Web User', 'web_user')
ON CONFLICT (user_id) DO NOTHING;

CREATE EXTENSION IF NOT EXISTS fuzzystrmatch
