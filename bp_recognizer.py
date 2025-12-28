# bp_recognizer.py
from roboflow import Roboflow


# ===============================
# 0️⃣ Roboflow 初始化（只會做一次）
# ===============================
rf = Roboflow(api_key="vII1juPnF7x7ZzztGCZl")  # ⚠️ 換成你的 Private API Key
workspace = rf.workspace("ns853851yahoocomtw")
project = workspace.project("number-0wvn3")
model = project.version(4).model


# ===============================
# 1️⃣ 主辨識函式（給 LINE 用）
# ===============================
def recognize_bp_from_image(image_path):
    """
    輸入：圖片路徑
    輸出：(SYS, DIA)
    """

    # -------- 1. Roboflow 預測 --------
    result = model.predict(
        image_path,
        confidence=0.4,
        overlap=0.3
    ).json()

    # -------- 2. 取出需要的欄位 --------
    predictions = [
        {
            "x": p["x"],
            "y": p["y"],
            "class": p["class"],
            "confidence": p["confidence"]
        }
        for p in result.get("predictions", [])
    ]

    if not predictions:
        return None, None

    # -------- 3. 先依 y 由上到下 --------
    predictions.sort(key=lambda p: p["y"])

    # -------- 4. 分 row（y 在誤差內視為同排） --------
    y_tolerance = 100
    rows = []

    for p in predictions:
        placed = False
        for row in rows:
            avg_y = sum(r["y"] for r in row) / len(row)
            if abs(avg_y - p["y"]) <= y_tolerance:
                row.append(p)
                placed = True
                break
        if not placed:
            rows.append([p])

    # -------- 5. rows 本身由上到下 --------
    rows.sort(key=lambda row: sum(p["y"] for p in row) / len(row))

    # -------- 6. 每 row 由左到右 --------
    for row in rows:
        row.sort(key=lambda p: p["x"])

    # -------- 7. 將每一排轉成數字 --------
    numbers = []

    for row in rows:
        # 至少 2 位才像數字
        if len(row) >= 2:
            value = int("".join(p["class"] for p in row))
            numbers.append(value)

    # -------- 8. 用「數值規則」判斷 SYS / DIA --------
    SYS = None
    DIA = None

    for n in numbers:
        # SYS：通常 100–250
        if 100 <= n <= 250 and SYS is None:
            SYS = n
        # DIA：通常 40–150
        elif 40 <= n <= 150 and DIA is None:
            DIA = n

    return SYS, DIA
