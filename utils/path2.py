import heapq
import math
import cv2
import numpy as np
import random

# Constants
GRID_SIZE_CM = 26
FIELD_WIDTH_CM = 1000
FIELD_HEIGHT_CM = 500
GRID_WIDTH = FIELD_WIDTH_CM // GRID_SIZE_CM
GRID_HEIGHT = FIELD_HEIGHT_CM // GRID_SIZE_CM

# Obstacle and Bot Settings
ball_radius = 5
bot_radius = 15
safe_margin = 10  # Extra margin around obstacles
immediate_safe_distance = 12  # Buffer zone around bot's starting position

# Global variables
bot_position = (320, 240)
goal_post_pos = (900, 240)
trimmed_area_selected = False
trimmed_area = []
balls = []
opponent_bots = []
path = []
extension_factor_before = 0.20
extension_factor_after = 0.20
buffer_distance = 20
update_path = False  # Track bot position changes

# Helper Functions
def generate_random_positions(count, exclusion_pos, radius):
    positions = []
    for _ in range(count):
        while True:
            pos = (random.randint(0, FIELD_WIDTH_CM), random.randint(0, FIELD_HEIGHT_CM))
            if math.dist(pos, exclusion_pos) > (radius + 50):
                positions.append(pos)
                break
    return positions

def select_corners(event, x, y, flags, param):
    global bot_position, trimmed_area, trimmed_area_selected, update_path
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(trimmed_area) < 4:
            trimmed_area.append((x, y))
            if len(trimmed_area) == 4:
                trimmed_area_selected = True
        else:
            bot_position = (x, y)
            update_path = True  # Trigger path update

def draw_grid(frame):
    for x in range(0, FIELD_WIDTH_CM, GRID_SIZE_CM):
        cv2.line(frame, (x, 0), (x, FIELD_HEIGHT_CM), (200, 200, 200), 1)
    for y in range(0, FIELD_HEIGHT_CM, GRID_SIZE_CM):
        cv2.line(frame, (0, y), (FIELD_WIDTH_CM, y), (200, 200, 200), 1)

def find_extended_points(ball_pos):
    dx, dy = goal_post_pos[0] - ball_pos[0], goal_post_pos[1] - ball_pos[1]
    length = math.sqrt(dx**2 + dy**2)
    if length == 0:
        return ball_pos, ball_pos

    dx, dy = dx / length, dy / length
    e1_dist = max(extension_factor_before * length, buffer_distance)
    e2_dist = max(extension_factor_after * length, buffer_distance)
    e1 = (int(ball_pos[0] - e1_dist * dx), int(ball_pos[1] - e1_dist * dy))
    e2 = (int(ball_pos[0] + e2_dist * dx), int(ball_pos[1] + e2_dist * dy))
    return e1, e2

def draw_objects(frame):
    for ball in balls:
        cv2.circle(frame, ball, ball_radius, (0, 255, 255), -1)
        e1, e2 = find_extended_points(ball)
        cv2.circle(frame, e1, 5, (0, 0, 255), -1)
        cv2.circle(frame, e2, 5, (255, 0, 0), -1)

    for bot in opponent_bots:
        cv2.circle(frame, bot, bot_radius, (255, 0, 0), -1)

    cv2.circle(frame, goal_post_pos, 15, (0, 255, 0), -1)

def enlarge_obstacle_area(grid, pos, radius):
    cx, cy = pos
    grid_x = cx // GRID_SIZE_CM
    grid_y = cy // GRID_SIZE_CM
    margin_cells = (radius + safe_margin) // GRID_SIZE_CM

    for dx in range(-margin_cells, margin_cells + 1):
        for dy in range(-margin_cells, margin_cells + 1):
            nx, ny = grid_x + dx, grid_y + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                if math.sqrt(dx**2 + dy**2) * GRID_SIZE_CM <= (radius + safe_margin):
                    grid[ny, nx] = 1

def create_exclusion_zone(grid, center, exclusion_radius):
    cx, cy = center
    grid_x, grid_y = cx // GRID_SIZE_CM, cy // GRID_SIZE_CM
    margin_cells = exclusion_radius // GRID_SIZE_CM

    for dx in range(-margin_cells, margin_cells + 1):
        for dy in range(-margin_cells, margin_cells + 1):
            nx, ny = grid_x + dx, grid_y + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                if math.sqrt(dx**2 + dy**2) * GRID_SIZE_CM <= exclusion_radius:
                    grid[ny, nx] = 1

# A* pathfinding algorithm
def find_path(grid, start, end):
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, end)}
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for dx, dy in directions:
            neighbor = (current[0] + dx, current[1] + dy)
            cost = math.sqrt(dx**2 + dy**2)
            tentative_g_score = g_score[current] + cost

            if 0 <= neighbor[0] < GRID_WIDTH and 0 <= neighbor[1] < GRID_HEIGHT:
                if grid[neighbor[1], neighbor[0]] != 0:
                    continue
                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, end)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return []

def process_frame(frame):
    global path, update_path
    if not update_path:
        return

    grid = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=int)

    # Mark obstacles with safe margin
    for ball in balls:
        enlarge_obstacle_area(grid, ball, ball_radius)
    for bot in opponent_bots:
        enlarge_obstacle_area(grid, bot, bot_radius)

    # Exclusion zone near the bot
    create_exclusion_zone(grid, bot_position, immediate_safe_distance)

    # Find nearest ball and determine extended points
    nearest_ball = min(balls, key=lambda b: math.dist(goal_post_pos, b))
    e1, e2 = find_extended_points(nearest_ball)
    bot_grid_pos = (bot_position[0] // GRID_SIZE_CM, bot_position[1] // GRID_SIZE_CM)
    e1_grid_pos = (e1[0] // GRID_SIZE_CM, e1[1] // GRID_SIZE_CM)

    # Find the initial path using A* algorithm
    path = find_path(grid, bot_grid_pos, e1_grid_pos)

    if path:
        # Convert path grid coordinates to actual field coordinates
        travel_coordinates = [(x * GRID_SIZE_CM, y * GRID_SIZE_CM) for x, y in path]

        # Print travel coordinates
        print("Travel Coordinates to Reach the Target (in cm):", travel_coordinates)

        # Draw the path on the frame
        for i in range(len(travel_coordinates) - 1):
            start = travel_coordinates[i]
            end = travel_coordinates[i + 1]
            cv2.line(frame, start, end, (255, 255, 0), 2)  # Draw path in cyan

    else:
        print("No valid path found.")

    update_path = False  # Reset after processing

# Sample bot and ball positions
balls = generate_random_positions(5, (500, 250), ball_radius)
opponent_bots = generate_random_positions(3, (500, 250), bot_radius)

# Create a window for visualization
cv2.namedWindow("Robot Path Planning")
cv2.setMouseCallback("Robot Path Planning", select_corners)

# Simulate the pathfinding process
while True:
    frame = np.zeros((FIELD_HEIGHT_CM, FIELD_WIDTH_CM, 3), dtype=np.uint8)

    # Draw grid, obstacles, and the bot
    draw_grid(frame)
    draw_objects(frame)

    # Process frame to find the path
    process_frame(frame)

    # Display the frame
    cv2.imshow("Robot Path Planning", frame)

    # Wait for key press to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
