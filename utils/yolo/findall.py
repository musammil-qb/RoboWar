from ultralytics import YOLO

model = YOLO("yolo/best.pt")

def findall(frame):
    result = model.predict(frame, conf=0.5)
    balls = []
    bot = None
    arena = None

    for r in result:
        boxes = r.boxes

        for box in boxes:
            if int(box.cls[0]) == 0: # Detect balls
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                center_point_ball = (int((x1+x2)/2), int((y1+y2)/2))

                balls.append(center_point_ball)

            if int(box.cls[0]) == 1: # Detect bot
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                center_point_bot = (int((x1+x2)/2), int((y1+y2)/2))

                bot = center_point_bot

            if int(box.cls[0]) == 2: # Detect arena
                x1, y1, x2, y2 = box.xyxy[0]
                arena = [int(i) for i in [x1, y1, x2, y2]]

    return balls, bot, arena