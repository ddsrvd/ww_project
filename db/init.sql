-- Таблица треков
CREATE TABLE IF NOT EXISTS tracks (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(20) NOT NULL,
    platform_track_id VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    artist VARCHAR(500) NOT NULL,
    album VARCHAR(500),
    duration_ms INTEGER,
    cover_url TEXT,
    preview_url TEXT,
    external_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(platform, platform_track_id)
);

-- Таблица рецензий
CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    track_id INTEGER REFERENCES tracks(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,
    user_name VARCHAR(255),
    rating INTEGER CHECK (rating >= 1 AND rating <= 10),
    review_text TEXT NOT NULL,
    source VARCHAR(20) NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

