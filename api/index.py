from flask import Flask, jsonify, request, send_file
import psycopg2
import psycopg2.extras
import os
app = Flask(__name__)

# Neon Database URL
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# --- Union-Find & Kruskal's Logic ---
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
def home():
    # Find the absolute path to the root folder where index.html is sitting
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    html_path = os.path.join(project_root, 'index.html')
    
    return send_file(html_path)

@app.route('/api/movies', methods=['GET'])
def get_movies():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM movies ORDER BY id ASC;")
    movies = [dict(row) for row in cursor.fetchall()]
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
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM movies ORDER BY id ASC;")
    movies = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    n = len(movies)
    all_edges = []

    for i in range(n):
        for j in range(i + 1, n):
            w = calc_weight(movies[i], movies[j])
            all_edges.append({"u": i, "v": j, "w": w})

    sorted_edges = sorted(all_edges, key=lambda x: x['w'])
    uf = UnionFind(n)
    mst = []
    steps = [{"type": "start", "text": f"Sorted {len(sorted_edges)} edges. Starting Kruskal's on {n} nodes."}]

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

    return jsonify({
        "movies": movies,
        "allEdges": all_edges,
        "mstEdges": mst,
        "steps": steps,
        "totalWeight": round(sum(e['w'] for e in mst), 2)
    })