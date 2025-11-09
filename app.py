import requests
from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

# maps your tracker tags → MyAnimeList genre IDs
GENRE_MAP = {
    "Action": 1,
    "Adventure": 2,
    "Comedy": 4,
    "Drama": 8,
    "Fantasy": 10,
    "Romance": 22,
    "Sci-Fi": 24,
    "Mystery": 7,
    "Thriller": 46,
    "Horror": 14,
    "Slice of Life": 36,
    "Supernatural": 37,
    "Historical": 11,
    "Psychological": 40,
    "Tragedy": 41,
    "Sports": 30,
    "Mecha": 18,
    "Military": 35,
    "Music": 19,
    "Magic": 20,
    "Martial Arts": 39
}


app = Flask(__name__)
app.secret_key = "super_secret_key_here"
DB_NAME = "anime.db"


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# Home page, list all entries
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    conn = get_db()
    cur = conn.cursor()

    search_query = request.args.get("q", "").strip()
    sort_by = request.args.get("sort", "alpha")
    genre_filter = request.args.get("genre", "").strip()
    progress_filter = request.args.get("progress", "").strip()
    page = int(request.args.get("page", 1))
    per_page = 9
    offset = (page - 1) * per_page

    sql = "SELECT * FROM anime WHERE user_id = ?"  # only user's anime
    params = [user_id]
    conditions = []

    if search_query:
        conditions.append("title LIKE ?")
        params.append(f"%{search_query}%")
    if genre_filter:
        conditions.append("tags LIKE ?")
        params.append(f"%{genre_filter}%")
    if progress_filter:
        conditions.append("progress LIKE ?")
        params.append(f"%{progress_filter}%")

    if conditions:
        sql += " AND " + " AND ".join(conditions)

    if sort_by == "rating":
        sql += " ORDER BY rating DESC"
    else:
        sql += " ORDER BY title ASC"

    sql += " LIMIT ? OFFSET ?"
    params.extend([per_page, offset])

    cur.execute(sql, params)
    anime_list = cur.fetchall()

    # Count total for pagination
    count_sql = "SELECT COUNT(*) FROM anime WHERE user_id = ?"
    count_params = [user_id]
    if conditions:
        count_sql += " AND " + " AND ".join(conditions)
        count_params += params[1:-2]  # skip LIMIT & OFFSET
    cur.execute(count_sql, count_params)
    total_items = cur.fetchone()[0]
    total_pages = (total_items + per_page - 1) // per_page

    cur.execute("SELECT tags FROM anime WHERE user_id = ?", (user_id,))
    all_tags = [tag for row in cur.fetchall() for tag in (
        row["tags"].split(", ") if row["tags"] else [])]
    genres_list = sorted(list(set(all_tags)))

    conn.close()

    return render_template(
        "index.html",
        anime_list=anime_list,
        search_query=search_query,
        current_sort=sort_by,
        current_genre=genre_filter,
        current_progress=progress_filter,
        genres_list=genres_list,
        page=page,
        total_pages=total_pages
    )



# Add new anime/manhwa
@app.route("/add", methods=["GET", "POST"])
def add():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form.get("title")
        progress = request.form.get("progress")
        rating = request.form.get("rating")
        image_url = request.form.get("image_url")
        comments = request.form.get("comments")
        type_ = request.form.get("type")
        tags = request.form.getlist("tags")
        tags_str = ", ".join(tags)
        user_id = session["user_id"]  # link to the logged-in user

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO anime (title, progress, rating, image_url, comments, type, tags, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, progress, rating, image_url, comments, type_, tags_str, user_id))
        conn.commit()
        conn.close()

        return redirect("/")
    return render_template("add.html")


# Edit anime/manhwa
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db()
    cur = conn.cursor()

    # Get the anime entry
    cur.execute("SELECT * FROM anime WHERE id = ?", (id,))
    anime = cur.fetchone()

    if not anime:
        conn.close()
        return "Anime not found", 404

    # Check if the current user owns this anime
    if anime["user_id"] != session["user_id"]:
        conn.close()
        flash("You can only edit your own entries.", "error")
        return redirect("/")

    if request.method == "POST":
        title = request.form.get("title")
        progress = request.form.get("progress")
        rating = request.form.get("rating")
        image_url = request.form.get("image_url")
        comments = request.form.get("comments")
        type_ = request.form.get("type")
        tags = request.form.getlist("tags")  # multiple genres selected
        tags_str = ", ".join(tags)

        cur.execute("""
            UPDATE anime
            SET title = ?, progress = ?, rating = ?, image_url = ?, comments = ?, type = ?, tags = ?
            WHERE id = ?
        """, (title, progress, rating, image_url, comments, type_, tags_str, id))

        conn.commit()
        conn.close()
        return redirect("/")

    conn.close()
    return render_template("edit.html", anime=anime)



# Delete an entry
@app.route("/delete/<int:id>")
def delete(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM anime WHERE id = ? AND user_id = ?", (id, session["user_id"]))
    conn.commit()
    conn.close()
    return redirect("/")


# Signup
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")

        conn = get_db()
        cur = conn.cursor()

        # Check if username already exists
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            flash("❌ User already exists. Please log in instead.", "error")
            conn.close()
            return redirect(url_for("signup"))

        hashed_pw = generate_password_hash(password)
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        conn.close()

        flash("✅ Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password")

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        conn.close()

        if not user:
            flash("🚫 User does not exist.", "error")
            return redirect(url_for("login"))

        if not check_password_hash(user["password"], password):
            flash("🔒 Incorrect password.", "error")
            return redirect(url_for("login"))

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        flash(f"👋 Welcome back, {user['username']}!", "success")
        return redirect(url_for("index"))

    return render_template("login.html")


# Logout
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for("login"))

@app.route("/recommendations")
def recommendations():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()

    # Get all user anime
    cur.execute("SELECT * FROM anime WHERE user_id = ?", (session["user_id"],))
    user_anime = cur.fetchall()
    user_titles = [anime["title"] for anime in user_anime]

    # Compute top tags weighted by rating
    tag_scores = {}
    for anime in user_anime:
        if anime["tags"]:
            tags = anime["tags"].split(", ")
            rating = int(anime["rating"])
            for tag in tags:
                tag_scores[tag] = tag_scores.get(tag, 0) + rating

    # Top 5 tags
    preferred_tags = sorted(tag_scores.items(), key=lambda x: x[1], reverse=True)
    top_tags = [tag for tag, score in preferred_tags[:5]]

    recommended = []

    # Local recommendations (anime not in user's list)
    if top_tags:
        like_conditions = " OR ".join(["tags LIKE ?" for _ in top_tags])
        params = [f"%{tag}%" for tag in top_tags]
        cur.execute(
            f"SELECT * FROM anime WHERE title NOT IN ({','.join(['?']*len(user_titles))}) AND ({like_conditions})",
            user_titles + params
        )
        local_candidates = cur.fetchall()

        for anime in local_candidates:
            if not anime["tags"]:
                continue
            candidate_tags = set(anime["tags"].split(", "))
            overlap = len(candidate_tags.intersection(top_tags))
            score = int(anime["rating"]) * overlap
            recommended.append((score, anime))

    # External recommendations from Jikan
    for tag in top_tags:
        genre_id = GENRE_MAP.get(tag)
        if not genre_id:
            continue
        url = "https://api.jikan.moe/v4/anime"
        params = {"genres": genre_id, "order_by": "score", "sort": "desc", "limit": 5}
        resp = requests.get(url, params=params)
        data = resp.json().get("data", [])
        for anime in data:
            if anime["title"] in user_titles:
                continue
            candidate_tags = set([g["name"] for g in anime.get("genres", [])])
            overlap = len(candidate_tags.intersection(top_tags))
            score = (anime.get("score") or 0) * overlap
            recommended.append((score, {
                "title": anime["title"],
                "type": anime.get("type", "Anime"),
                "rating": anime.get("score", 0),
                "image_url": anime["images"]["jpg"]["image_url"],
                "tags": ", ".join([g["name"] for g in anime.get("genres", [])]),
                "comments": ""
            }))

    # Sort by score descending and pick top 20
    recommended.sort(key=lambda x: x[0], reverse=True)
    recommended = [anime for score, anime in recommended][:20]

    conn.close()

    return render_template("recommendations.html", recommended=recommended, top_tags=top_tags)

def create_users_table():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_users_table()
    app.run(debug=True)
