import cv2
import numpy as np

# Function to detect objects based on color
def detect_objects(frame, playground_color_range, yellow_bot_range, yellow_ball_range, opponent_bot_range):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Detect playground (dominant color as background)
    playground_mask = cv2.inRange(hsv, playground_color_range[0], playground_color_range[1])

    # Detect yellow bot
    bot_mask = cv2.inRange(hsv, yellow_bot_range[0], yellow_bot_range[1])

    # Detect yellow balls
    ball_mask = cv2.inRange(hsv, yellow_ball_range[0], yellow_ball_range[1])

    # Detect opponent bot (assuming a color distinct from the bot and playground)
    opponent_mask = cv2.inRange(hsv, opponent_bot_range[0], opponent_bot_range[1])

    # Remove playground from bot, ball, and opponent detection
    bot_mask = cv2.bitwise_and(bot_mask, bot_mask, mask=cv2.bitwise_not(playground_mask))
    ball_mask = cv2.bitwise_and(ball_mask, ball_mask, mask=cv2.bitwise_not(playground_mask))
    opponent_mask = cv2.bitwise_and(opponent_mask, opponent_mask, mask=cv2.bitwise_not(playground_mask))

    # Find contours for bot, ball, and opponent
    contours_bot, _ = cv2.findContours(bot_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_ball, _ = cv2.findContours(ball_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_opponent, _ = cv2.findContours(opponent_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return contours_bot, contours_ball, contours_opponent

# Function to detect goalposts based on the arena's geometry
def detect_goalpost(frame):
    height, width, _ = frame.shape
    goalpost_left = (int(width * 0.05), int(height / 2))  # Left goalpost
    goalpost_right = (int(width * 0.95), int(height / 2))  # Right goalpost
    return goalpost_left, goalpost_right

# Function to calculate distance and angle between two points
def calculate_distance_angle(point1, point2):
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    distance = np.sqrt(dx**2 + dy**2)
    angle = np.arctan2(dy, dx) * 180 / np.pi
    return distance, angle

# Function to find nearest unblocked ball
def find_nearest_ball(bot_center, ball_centers, opponent_center):
    distances = []
    for ball_center in ball_centers:
        # Check if the ball is blocked by the opponent bot
        if opponent_center is not None:
            distance_to_opponent, _ = calculate_distance_angle(bot_center, opponent_center)
            distance_to_ball, _ = calculate_distance_angle(bot_center, ball_center)
            if distance_to_opponent < distance_to_ball:
                # If opponent is closer to the bot than the ball, skip this ball (blocked)
                continue
        distance, angle = calculate_distance_angle(bot_center, ball_center)
        distances.append((distance, ball_center, angle))

    # Sort balls by distance (greedy approach)
    distances.sort(key=lambda x: x[0])
    return distances[0] if distances else (None, None, None)

# Main function to run the bot detection and movement logic
def main():
    cap = cv2.VideoCapture(0)

    # Define the color ranges for playground, bot, ball, and opponent in HSV
    playground_color_range = [(35, 40, 40), (85, 255, 255)]  # Example green playground
    yellow_bot_range = [(25, 100, 100), (35, 255, 255)]  # Yellow square for bot
    yellow_ball_range = [(20, 100, 100), (30, 255, 255)]  # Yellow circle for balls
    opponent_bot_range = [(0, 100, 100), (10, 255, 255)]  # Example red for opponent bot

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Detect objects (bot, balls, opponent)
        contours_bot, contours_ball, contours_opponent = detect_objects(
            frame, playground_color_range, yellow_bot_range, yellow_ball_range, opponent_bot_range)

        # Detect goalposts
        goalpost_left, goalpost_right = detect_goalpost(frame)

        # Draw goalposts
        cv2.circle(frame, goalpost_left, 10, (255, 0, 0), -1)  # Blue left goalpost
        cv2.circle(frame, goalpost_right, 10, (255, 0, 0), -1)  # Blue right goalpost

        bot_center = None
        ball_centers = []
        opponent_center = None

        # Process bot contours
        for contour in contours_bot:
            if cv2.contourArea(contour) > 500:  # Filter small contours
                x, y, w, h = cv2.boundingRect(contour)
                bot_center = (x + w // 2, y + h // 2)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green for bot

        # Process ball contours (limit to 10 balls)
        for contour in contours_ball:
            if len(ball_centers) < 10 and cv2.contourArea(contour) > 100:  # Filter small contours
                (x, y), radius = cv2.minEnclosingCircle(contour)
                ball_center = (int(x), int(y))
                ball_centers.append(ball_center)
                cv2.circle(frame, ball_center, int(radius), (0, 255, 255), 2)  # Yellow for balls

        # Process the opponent bot contours (we'll take only the largest one)
        if contours_opponent:
            largest_opponent = max(contours_opponent, key=cv2.contourArea)
            if cv2.contourArea(largest_opponent) > 500:  # Filter small contours
                x, y, w, h = cv2.boundingRect(largest_opponent)
                opponent_center = (x + w // 2, y + h // 2)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Red for opponent bot

        # If bot is detected, find the nearest unblocked ball
        if bot_center is not None and ball_centers:
            nearest_distance, nearest_ball, nearest_angle = find_nearest_ball(bot_center, ball_centers, opponent_center)

            # Output positions of balls, opponent, and nearest ball
            print("Bot Position:", bot_center)
            for i, ball_center in enumerate(ball_centers):
                distance, _ = calculate_distance_angle(bot_center, ball_center)
                print(f"Ball {i+1} Position: {ball_center}, Distance: {distance:.2f}")

            if opponent_center is not None:
                print(f"Opponent Position: {opponent_center}")

            if nearest_ball is not None:
                print(f"Nearest Ball Position: {nearest_ball}, Distance: {nearest_distance:.2f}, Angle: {nearest_angle:.2f}")
                # Visualize path to nearest ball
                cv2.line(frame, bot_center, nearest_ball, (0, 255, 255), 2)

                # Decide movement based on the nearest ball's position
                if nearest_angle > 10:  # Example: if angle is greater than 10 degrees, turn right
                    print("Move Right")
                elif nearest_angle < -10:  # Example: if angle is less than -10 degrees, turn left
                    print("Move Left")
                else:
                    print("Move Forward")

        # Defend the goal if the opponent is near the goalpost
        if opponent_center is not None:
            distance_to_goal_left, _ = calculate_distance_angle(opponent_center, goalpost_left)
            distance_to_goal_right, _ = calculate_distance_angle(opponent_center, goalpost_right)

            if distance_to_goal_left < 100 or distance_to_goal_right < 100:  # Opponent near goal
                print("Defend the Goal")

        # Display the result
        cv2.imshow('Arena', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
