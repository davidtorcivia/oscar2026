from models import get_db

CATEGORIES = [
    {
        "slug": "best-picture",
        "name": "Best Picture",
        "sort_order": 1,
        "num_nominees": 10,
        "nominees": [
            ("Bugonia", None),
            ("F1", None),
            ("Frankenstein", None),
            ("Hamnet", None),
            ("Marty Supreme", None),
            ("One Battle after Another", None),
            ("The Secret Agent", None),
            ("Sentimental Value", None),
            ("Sinners", None),
            ("Train Dreams", None),
        ],
    },
    {
        "slug": "directing",
        "name": "Directing",
        "sort_order": 2,
        "num_nominees": 5,
        "nominees": [
            ("Chloe Zhao", "Hamnet"),
            ("Josh Safdie", "Marty Supreme"),
            ("Paul Thomas Anderson", "One Battle after Another"),
            ("Joachim Trier", "Sentimental Value"),
            ("Ryan Coogler", "Sinners"),
        ],
    },
    {
        "slug": "actor-leading",
        "name": "Actor in a Leading Role",
        "sort_order": 3,
        "num_nominees": 5,
        "nominees": [
            ("Timothee Chalamet", "Marty Supreme"),
            ("Leonardo DiCaprio", "One Battle after Another"),
            ("Ethan Hawke", "Blue Moon"),
            ("Michael B. Jordan", "Sinners"),
            ("Wagner Moura", "The Secret Agent"),
        ],
    },
    {
        "slug": "actress-leading",
        "name": "Actress in a Leading Role",
        "sort_order": 4,
        "num_nominees": 5,
        "nominees": [
            ("Jessie Buckley", "Hamnet"),
            ("Rose Byrne", "If I Had Legs I'd Kick You"),
            ("Kate Hudson", "Song Sung Blue"),
            ("Renate Reinsve", "Sentimental Value"),
            ("Emma Stone", "Bugonia"),
        ],
    },
    {
        "slug": "actor-supporting",
        "name": "Actor in a Supporting Role",
        "sort_order": 5,
        "num_nominees": 5,
        "nominees": [
            ("Benicio Del Toro", "One Battle after Another"),
            ("Jacob Elordi", "Frankenstein"),
            ("Delroy Lindo", "Sinners"),
            ("Sean Penn", "One Battle after Another"),
            ("Stellan Skarsgard", "Sentimental Value"),
        ],
    },
    {
        "slug": "actress-supporting",
        "name": "Actress in a Supporting Role",
        "sort_order": 6,
        "num_nominees": 5,
        "nominees": [
            ("Elle Fanning", "Sentimental Value"),
            ("Inga Ibsdotter Lilleaas", "Sentimental Value"),
            ("Amy Madigan", "Weapons"),
            ("Wunmi Mosaku", "Sinners"),
            ("Teyana Taylor", "One Battle after Another"),
        ],
    },
    {
        "slug": "writing-original",
        "name": "Writing (Original Screenplay)",
        "sort_order": 7,
        "num_nominees": 5,
        "nominees": [
            ("Blue Moon", "Robert Kaplow"),
            ("It Was Just an Accident", "Jafar Panahi"),
            ("Marty Supreme", "Ronald Bronstein & Josh Safdie"),
            ("Sentimental Value", "Eskil Vogt, Joachim Trier"),
            ("Sinners", "Ryan Coogler"),
        ],
    },
    {
        "slug": "writing-adapted",
        "name": "Writing (Adapted Screenplay)",
        "sort_order": 8,
        "num_nominees": 5,
        "nominees": [
            ("Bugonia", "Will Tracy"),
            ("Frankenstein", "Guillermo del Toro"),
            ("Hamnet", "Chloe Zhao & Maggie O'Farrell"),
            ("One Battle after Another", "Paul Thomas Anderson"),
            ("Train Dreams", "Clint Bentley & Greg Kwedar"),
        ],
    },
    {
        "slug": "animated-feature",
        "name": "Animated Feature Film",
        "sort_order": 9,
        "num_nominees": 5,
        "nominees": [
            ("Arco", None),
            ("Elio", None),
            ("KPop Demon Hunters", None),
            ("Little Amelie or the Character of Rain", None),
            ("Zootopia 2", None),
        ],
    },
    {
        "slug": "animated-short",
        "name": "Animated Short Film",
        "sort_order": 10,
        "num_nominees": 5,
        "nominees": [
            ("Butterfly", None),
            ("Forevergreen", None),
            ("The Girl Who Cried Pearls", None),
            ("Retirement Plan", None),
            ("The Three Sisters", None),
        ],
    },
    {
        "slug": "international-feature",
        "name": "International Feature Film",
        "sort_order": 11,
        "num_nominees": 5,
        "nominees": [
            ("The Secret Agent", "Brazil"),
            ("It Was Just an Accident", "France"),
            ("Sentimental Value", "Norway"),
            ("Sirat", "Spain"),
            ("The Voice of Hind Rajab", "Tunisia"),
        ],
    },
    {
        "slug": "documentary-feature",
        "name": "Documentary Feature Film",
        "sort_order": 12,
        "num_nominees": 5,
        "nominees": [
            ("The Alabama Solution", None),
            ("Come See Me in the Good Light", None),
            ("Cutting through Rocks", None),
            ("Mr. Nobody against Putin", None),
            ("The Perfect Neighbor", None),
        ],
    },
    {
        "slug": "documentary-short",
        "name": "Documentary Short Film",
        "sort_order": 13,
        "num_nominees": 5,
        "nominees": [
            ("All the Empty Rooms", None),
            ("Armed Only with a Camera", None),
            ('Children No More: "Were and Are Gone"', None),
            ("The Devil Is Busy", None),
            ("Perfectly a Strangeness", None),
        ],
    },
    {
        "slug": "live-action-short",
        "name": "Live Action Short Film",
        "sort_order": 14,
        "num_nominees": 5,
        "nominees": [
            ("Butcher's Stain", None),
            ("A Friend of Dorothy", None),
            ("Jane Austen's Period Drama", None),
            ("The Singers", None),
            ("Two People Exchanging Saliva", None),
        ],
    },
    {
        "slug": "casting",
        "name": "Casting",
        "sort_order": 15,
        "num_nominees": 5,
        "nominees": [
            ("Nina Gold", "Hamnet"),
            ("Jennifer Venditti", "Marty Supreme"),
            ("Cassandra Kulukundis", "One Battle after Another"),
            ("Gabriel Domingues", "The Secret Agent"),
            ("Francine Maisler", "Sinners"),
        ],
    },
    {
        "slug": "cinematography",
        "name": "Cinematography",
        "sort_order": 16,
        "num_nominees": 5,
        "nominees": [
            ("Dan Laustsen", "Frankenstein"),
            ("Darius Khondji", "Marty Supreme"),
            ("Michael Bauman", "One Battle after Another"),
            ("Autumn Durald Arkapaw", "Sinners"),
            ("Adolpho Veloso", "Train Dreams"),
        ],
    },
    {
        "slug": "film-editing",
        "name": "Film Editing",
        "sort_order": 17,
        "num_nominees": 5,
        "nominees": [
            ("Stephen Mirrione", "F1"),
            ("Ronald Bronstein & Josh Safdie", "Marty Supreme"),
            ("Andy Jurgensen", "One Battle after Another"),
            ("Olivier Bugge Coutte", "Sentimental Value"),
            ("Michael P. Shawver", "Sinners"),
        ],
    },
    {
        "slug": "production-design",
        "name": "Production Design",
        "sort_order": 18,
        "num_nominees": 5,
        "nominees": [
            ("Frankenstein", None),
            ("Hamnet", None),
            ("Marty Supreme", None),
            ("One Battle after Another", None),
            ("Sinners", None),
        ],
    },
    {
        "slug": "costume-design",
        "name": "Costume Design",
        "sort_order": 19,
        "num_nominees": 5,
        "nominees": [
            ("Deborah L. Scott", "Avatar: Fire and Ash"),
            ("Kate Hawley", "Frankenstein"),
            ("Malgosia Turzanska", "Hamnet"),
            ("Miyako Bellizzi", "Marty Supreme"),
            ("Ruth E. Carter", "Sinners"),
        ],
    },
    {
        "slug": "makeup-hairstyling",
        "name": "Makeup and Hairstyling",
        "sort_order": 20,
        "num_nominees": 5,
        "nominees": [
            ("Frankenstein", None),
            ("Kokuho", None),
            ("Sinners", None),
            ("The Smashing Machine", None),
            ("The Ugly Stepsister", None),
        ],
    },
    {
        "slug": "sound",
        "name": "Sound",
        "sort_order": 21,
        "num_nominees": 5,
        "nominees": [
            ("F1", None),
            ("Frankenstein", None),
            ("One Battle after Another", None),
            ("Sinners", None),
            ("Sirat", None),
        ],
    },
    {
        "slug": "visual-effects",
        "name": "Visual Effects",
        "sort_order": 22,
        "num_nominees": 5,
        "nominees": [
            ("Avatar: Fire and Ash", None),
            ("F1", None),
            ("Jurassic World Rebirth", None),
            ("The Lost Bus", None),
            ("Sinners", None),
        ],
    },
    {
        "slug": "music-score",
        "name": "Music (Original Score)",
        "sort_order": 23,
        "num_nominees": 5,
        "nominees": [
            ("Jerskin Fendrix", "Bugonia"),
            ("Alexandre Desplat", "Frankenstein"),
            ("Max Richter", "Hamnet"),
            ("Jonny Greenwood", "One Battle after Another"),
            ("Ludwig Goransson", "Sinners"),
        ],
    },
    {
        "slug": "music-song",
        "name": "Music (Original Song)",
        "sort_order": 24,
        "num_nominees": 5,
        "nominees": [
            ('"Dear Me"', "Diane Warren - Relentless"),
            ('"Golden"', "KPop Demon Hunters"),
            ('"I Lied to You"', "Sinners"),
            ('"Sweet Dreams of Joy"', "Viva Verdi!"),
            ('"Train Dreams"', "Train Dreams"),
        ],
    },
]


def seed_db():
    db = get_db()
    count = db.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    if count > 0:
        db.close()
        return False  # Already seeded

    for cat in CATEGORIES:
        db.execute(
            "INSERT INTO categories (slug, name, sort_order, num_nominees) VALUES (?, ?, ?, ?)",
            (cat["slug"], cat["name"], cat["sort_order"], cat["num_nominees"]),
        )
        cat_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        for name, subtitle in cat["nominees"]:
            db.execute(
                "INSERT INTO nominees (category_id, name, subtitle) VALUES (?, ?, ?)",
                (cat_id, name, subtitle),
            )

    db.commit()
    db.close()
    return True
