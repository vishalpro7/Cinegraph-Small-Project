from flask import Flask, render_template, jsonify, request
import mysql.connector

app = Flask(__name__)

# Update these with your local MySQL credentials
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "password",
    "database": "cinegraph"
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# --- Python Implementation of Union-Find & Kruskal's ---
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py: return False
        if self.rank[px] < self.rank[py]: self.parent[px] = py
        elif self.rank[px] > self.rank[py]: self.parent[py] = px
        else:
            self.parent[py] = px
            self.rank[px] += 1
        return True

def calc_weight(movie_a, movie_b):
    rating_diff = abs(movie_a['rating'] - movie_b['rating'])
    genre_penalty = 2 if movie_a['genre'] != movie_b['genre'] else 0
    return round(rating_diff + genre_penalty, 2)

# --- Routes ---

@app.route('/')
def index():
    # Flask looks in the 'templates' folder automatically
    return render_template('index.html')

@app.route('/api/movies', methods=['GET'])
def get_movies():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM movies ORDER BY id ASC;")
    movies = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(movies)

@app.route('/api/recommend', methods=['POST'])
def recommend():
    data = request.json
    selected_id = data.get('movie_id')

    if selected_id is None:
        return jsonify({"error": "No movie selected"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM movies ORDER BY id ASC;")
    movies = cursor.fetchall()
    cursor.close()
    conn.close()

    n = len(movies)
    all_edges = []

    # Build all edges
    for i in range(n):
        for j in range(i + 1, n):
            w = calc_weight(movies[i], movies[j])
            all_edges.append({"u": i, "v": j, "w": w})

    # Sort edges
    sorted_edges = sorted(all_edges, key=lambda x: x['w'])
    uf = UnionFind(n)
    mst = []
    steps = []

    steps.append({"type": "start", "text": f"Sorted {len(sorted_edges)} edges. Starting Kruskal's on {n} nodes."})

    for edge in sorted_edges:
        u, v, w = edge['u'], edge['v'], edge['w']
        u_name = movies[u]['title']
        v_name = movies[v]['title']

        if uf.union(u, v):
            mst.append(edge)
            steps.append({"type": "added", "text": f"Added edge <strong>{u_name}</strong> — <strong>{v_name}</strong> (w={w})"})
            if len(mst) == n - 1:
                steps.append({"type": "start", "text": f"MST complete! Selected {len(mst)} edges."})
                break
        else:
            steps.append({"type": "skipped", "text": f"Skipped <strong>{u_name}</strong> — <strong>{v_name}</strong> (w={w}) — would form cycle"})

    total_weight = sum(e['w'] for e in mst)

    return jsonify({
        "movies": movies,
        "allEdges": all_edges,
        "mstEdges": mst,
        "steps": steps,
        "totalWeight": round(total_weight, 2)
    })

if __name__ == '__main__':
    app.run(debug=True)