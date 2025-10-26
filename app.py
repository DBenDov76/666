import os
import pandas as pd
import random
from itertools import combinations
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Utility: check primes
PRIMES = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37}

def read_file(filepath):
    if filepath.lower().endswith(".csv"):
        df = pd.read_csv(filepath, header=None)
    else:
        df = pd.read_excel(filepath, header=None)
    return df

def build_pool(df, exclude_10_20_30=False):
    numbers = list(range(1, 38))
    last_game = set(df.iloc[0].dropna().astype(int).tolist())
    removed = set()

    for num in numbers:
        recent4 = (df.head(4) == num).sum().sum()
        recent6 = (df.head(6) == num).sum().sum()
        recent10 = (df.head(10) == num).sum().sum()
        if recent4 >= 2 or recent6 >= 3 or recent10 >= 5:
            removed.add(num)

    pool = [n for n in numbers if n not in removed]

    # user option: exclude 10,20,30
    if exclude_10_20_30:
        pool = [n for n in pool if n not in {10, 20, 30}]
        removed.update({10, 20, 30})

    return pool, removed, last_game

def unseen_last10(df):
    last10 = df.head(10).values.flatten()
    last10 = pd.Series(last10).dropna().astype(int).tolist()
    unseen = [n for n in range(1, 38) if n not in last10]
    return unseen

def has_invalid_sequences(combo):
    """Return True if combo has more than 2 consecutive numbers
       or more than one pair of consecutive numbers."""
    sorted_combo = sorted(combo)
    consecutive_streak = 1
    consecutive_pairs = 0

    for i in range(1, len(sorted_combo)):
        if sorted_combo[i] == sorted_combo[i - 1] + 1:
            consecutive_streak += 1
            if consecutive_streak == 2:
                consecutive_pairs += 1
            if consecutive_streak > 2:
                return True  # found more than 2 consecutive
        else:
            consecutive_streak = 1

    # more than one pair of consecutive numbers
    if consecutive_pairs > 1:
        return True

    return False

def generate_combinations(pool, last_game, removed, unseen, df):
    valid = []
    tries = 0

    all_prev_combos = [set(df.iloc[i].dropna().astype(int).tolist()) for i in range(len(df))]

    last1000 = df.head(1000)
    five_sets = set()
    for row in last1000.itertuples(index=False):
        rownums = [int(x) for x in row if pd.notna(x)]
        for c in combinations(rownums, 5):
            five_sets.add(tuple(sorted(c)))

    last200 = df.head(200)
    four_sets = set()
    for row in last200.itertuples(index=False):
        rownums = [int(x) for x in row if pd.notna(x)]
        for c in combinations(rownums, 4):
            four_sets.add(tuple(sorted(c)))

    while len(valid) < 40 and tries < 20000:
        tries += 1
        combo = random.sample(pool, 6)
        combo_set = set(combo)

        # sequences rule
        if has_invalid_sequences(combo):
            continue

        if len(combo_set & last_game) > 1:
            continue
        unseen_count = len(combo_set & set(unseen))
        if unseen_count < 1 or unseen_count > 2:
            continue
        if 1 in combo_set and 37 in combo_set:
            continue
        if not (combo_set & PRIMES):
            continue
        if len(combo_set & {10, 20, 30}) > 1:
            continue
        evens = len([n for n in combo if n % 2 == 0])
        odds = 6 - evens
        if evens > 4 or odds > 4:
            continue
        total = sum(combo)
        if total < 83 or total > 142:
            continue
        if combo_set in all_prev_combos:
            continue
        if any(tuple(sorted(c)) in five_sets for c in combinations(combo, 5)):
            continue
        if any(tuple(sorted(c)) in four_sets for c in combinations(combo, 4)):
            continue

        valid.append(sorted(combo))

    return valid

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        if not file:
            return render_template("index.html", error="No file uploaded")
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        df = read_file(filepath)
        exclude_10_20_30 = "exclude_10_20_30" in request.form

        pool, removed, last_game = build_pool(df, exclude_10_20_30)
        unseen = unseen_last10(df)
        combos = generate_combinations(pool, last_game, removed, unseen, df)

        return render_template(
            "index.html",
            pool=pool,
            removed=sorted(list(removed)),
            last_game=list(last_game),
            unseen=unseen,
            combos=combos
        )
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    combos = request.form.get("combos")
    if not combos:
        return "No data to download", 400
    import io
    import csv
    output = io.StringIO()
    writer = csv.writer(output)
    for row in eval(combos):
        writer.writerow(row)
    mem = io.BytesIO()
    mem.write(output.getvalue().encode("utf-8"))
    mem.seek(0)
    output.close()
    return send_file(mem, mimetype="text/csv", as_attachment=True, download_name="combinations.csv")

if __name__ == "__main__":
    # IMPORTANT for Render.com: bind to 0.0.0.0 and use the assigned PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
