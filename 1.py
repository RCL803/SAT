import cv2
from roboflow import Roboflow

# ===============================
# 0️⃣ Roboflow 初始化
# ===============================

rf = Roboflow(api_key="vII1juPnF7x7ZzztGCZl")  # Private API Key
workspace = rf.workspace("ns853851yahoocomtw")
project = workspace.project("number-0wvn3")
model = project.version(4).model

# ===============================
# 1️⃣ 用模型預測圖片（⚠️ 關鍵）
# ===============================
result = model.predict(
    "111.jpg",
    confidence=40,
    overlap=30
).json()

# ===============================
# 2️⃣ 轉成你原本使用的 predictions 格式
# ===============================
predictions = [
    {
        "x": p["x"],
        "y": p["y"],
        "width": p["width"],
        "height": p["height"],
        "confidence": p["confidence"],
        "class": p["class"]
    }
    for p in result["predictions"]
]

# ===============================
# 3️⃣ 先依 y 由上到下排序（很重要）
# ===============================
predictions = sorted(predictions, key=lambda p: p["y"])

y_tolerance = 100
rows = []

# ===============================
# 4️⃣ 分 row（y 在誤差內視為同排）
# ===============================
for p in predictions:
    placed = False
    for row in rows:
        row_y = sum(r["y"] for r in row) / len(row)
        if abs(row_y - p["y"]) <= y_tolerance:
            row.append(p)
            placed = True
            break
    if not placed:
        rows.append([p])

# ===============================
# 5️⃣ rows 本身依 y 排序（確保第一排是最上面）
# ===============================
rows.sort(key=lambda row: sum(p["y"] for p in row) / len(row))

# ===============================
# 6️⃣ 每一排內依 x 由左到右
# ===============================
for row in rows:
    row.sort(key=lambda p: p["x"])

# ===============================
# 7️⃣ 印出結果（你要的順序）
# ===============================
for i, row in enumerate(rows, 1):
    values = "".join(p["class"] for p in row)
    print(f"Row {i}: {values}")

def row_to_number(row):
    """
    將一排 row（已經依 x 排序）轉成整數
    例如 ["1","0","9"] → 109
    """
    return int("".join(p["class"] for p in row))

SYS = row_to_number(rows[0])
DIA = row_to_number(rows[1])


print(f"SYS={SYS}, DIA={DIA}")
# ===============================
# 8️⃣ 畫框顯示
# ===============================
image = cv2.imread("333.jpg")

for row in rows:
    for p in row:
        x, y, w, h = int(p["x"]), int(p["y"]), int(p["width"]), int(p["height"])
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(
            image,
            f"{p['class']} {p['confidence']:.2f}",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            1
        )

cv2.imwrite("output_with_predictions_sorted.png", image)
print("已輸出圖片：output_with_predictions_sorted.png")

