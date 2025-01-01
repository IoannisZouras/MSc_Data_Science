# --------------------------------- IMPORTING LIBRARIES ---------------------------------


import os
import copy
import cv2
import numpy as np
from collections import Counter


# --------------------------------- FUNCTION DEFINITIONS ---------------------------------


# --------------------------------- HELPER FUNCTIONS ---------------------------------


# Use as a place holder
def nothing(x):
    pass


# Use for showing images, with waitKey(0) and then destroying the window
def show_image_with_waitkey(image, window_name="Image"):
    cv2.imshow(window_name, image)
    cv2.waitKey(0)
    cv2.destroyWindow("Image")
    
    
# Check if a point is within a mask
def is_point_in_mask(mask, point):
    x, y = point
    return mask[y, x] != 0  # Assuming (x, y) is in (column, row) format
    
  
# Convert a chess square (e.g., "A1") to board indices (row, col)
def position_to_indices(square):
    col = ord(square[0].upper()) - ord('A')  # Convert 'A'-'H' to 0-7
    row = 8 - int(square[1])  # Convert '1'-'8' to 7-0
    return row, col


# Convert board indices (row, col) to a chess square (e.g., "A1")
def indices_to_position(row, col):
    return f"{chr(col + ord('A'))}{8 - row}"
    

# Paint centers and annotate squares in an image
def paint_centers_and_squares(image, squares_centers_dict):
    for square, center in squares_centers_dict.items():
        cv2.circle(image, center, 5, (0,0,255), -1)  # Paint a red filled circle
        cv2.putText(image, square, (center[0] - 20, center[1] + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1, cv2.LINE_AA) # Annotate the chessboard square
                                    
    return image

                                    
# Access specific space on the chessboard matrix
def get_piece_at_square(board_matrix, square):
    row, col = position_to_indices(square)
    return board_matrix[row][col]
    
    
# Chessboard initialization
def initialize_chessboard():
    
    chessboard = [
        ["bR1", "bN", "bB", "bQ", "bK", "bB", "bN", "bR2"],  # Black major pieces
        ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],  # Black pawns
        [None, None, None, None, None, None, None, None],  # Empty row
        [None, None, None, None, None, None, None, None],  # Empty row
        [None, None, None, None, None, None, None, None],  # Empty row
        [None, None, None, None, None, None, None, None],  # Empty row
        ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],  # White pawns
        ["wR1", "wN", "wB", "wQ", "wK", "wB", "wN", "wR2"],  # White major pieces
    ]
    
    '''
    # Pawn promotion testing chessboard
    chessboard = [
        ["bR1", "bN", "bB", "bQ", "bK", "bB", "bN", None],  # Black major pieces
        ["bP", "bP", "bP", "bP", "bP", "bP", "wP", "wP"],  # Black pawns
        [None, None, None, None, None, None, None, None],  # Empty row
        [None, None, None, None, None, "wP", None, None],  # Empty row
        [None, None, None, None, None, None, None, None],  # Empty row
        [None, None, None, None, None, None, None, None],  # Empty row
        ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],  # White pawns
        ["wR1", "wN", "wB", "wQ", "wK", "wB", "wN", "wR2"],  # White major pieces
    ]
    
    # En passant testing chessboard
    chessboard = [
        ["bR1", "bN", "bB", "bQ", "bK", "bB", "bN", "bR2"],  # Black major pieces
        ["bP", "bP", "bP", "bP", "bP", "bP", "wP", "bP"],  # Black pawns
        [None, None, None, None, None, None, None, None],  # Empty row
        [None, None, None, None, None, "wP", None, None],  # Empty row
        [None, None, None, None, None, None, None, None],  # Empty row
        [None, None, None, None, None, None, None, None],  # Empty row
        ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],  # White pawns
        ["wR1", "wN", "wB", "wQ", "wK", "wB", "wN", "wR2"],  # White major pieces
    ]
    
   
    # Castling testing chessboard
    chessboard = [
        ["bR1", None, None, None, "bK", "bB", "bN", "bR2"],  # Black major pieces
        ["bP", "wP", "bP", "bP", "bP", "bP", "wP", "bP"],  # Black pawns
        [None, None, "bB", None, None, None, None, None],  # Empty row
        [None, None, None, None, None, None, None, None],  # Empty row
        [None, None, None, None, None, None, None, None],  # Empty row
        [None, None, None, None, None, None, None, None],  # Empty row
        ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],  # White pawns
        ["wR1", "wN", "wB", "wQ", "wK", None, None, "wR2"],  # White major pieces
    ]
    
    # Special moves testing chessboard
    chessboard = [
        [None, "bN", "bB", "bQ", "bK", None, None, "bR2"],  # Black major pieces
        ["wP", "bP", "bP", None, "bP", "bP", "bP", "bP"],  # Black pawns
        [None, None, None, None, None, None, None, None],  # Empty row
        [None, None, None, None, None, None, None, None],  # Empty row
        [None, None, None, "bP", None, None, None, None],  # Empty row
        [None, None, None, None, None, None, None, None],  # Empty row
        [None, "wP", "wP", "wP", "wP", "wP", "wP", "wP"],  # White pawns
        ["wR1", None, None, None, "wK", "wB", "wN", "wR2"],  # White major pieces
    ]
    '''
    
    return chessboard
    
    
# Move a piece from one square to another
def move_piece(board_matrix, start, end):
    # Get the piece at the start square
    piece = get_piece_at_square(board_matrix, start)
    # Get the indices for the start and end positions
    start_row, start_col = position_to_indices(start)
    end_row, end_col = position_to_indices(end)
    
    # If there is a piece at the start square, move it to the end square
    if piece:
        board_matrix[end_row][end_col] = piece  # Place piece at the new square
        board_matrix[start_row][start_col] = None  # Empty the start square
    else:
        print(f"No piece at {start} to move.\n")
        
    
# --------------------------------- DRAW CHESSBOARD FUNCTIONS ---------------------------------


# Draw a chessboard with custom light and dark square colors, and add labels
def draw_chessboard_with_labels(custom_light_color=(181, 217, 240), custom_dark_color=(99, 136, 181)):
    board = np.zeros((BOARD_SIZE + SQUARE_SIZE, BOARD_SIZE + SQUARE_SIZE, 3), dtype=np.uint8) # Create a blank canvas with extra space for labels
    board.fill(255) # Set background to white
    
    # Draw the grid
    for row in range(8):
        for col in range(8):
            x_start = col * SQUARE_SIZE + SQUARE_SIZE
            y_start = row * SQUARE_SIZE
            color = custom_light_color if (row + col) % 2 == 0 else custom_dark_color
            cv2.rectangle(board, (x_start, y_start), (x_start + SQUARE_SIZE, y_start + SQUARE_SIZE), color, -1)

    # Add row numbers (1-8)
    for row in range(8):
        label = str(8 - row) # Top to bottom to follow chess numbering 
        y = row * SQUARE_SIZE + SQUARE_SIZE // 2
        cv2.putText(board, label, (10, y + 10), FONT, FONT_SCALE, TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)

    # Add column letters (A-H)
    for col in range(8):
        label = chr(ord('A') + col)  
        x = col * SQUARE_SIZE + SQUARE_SIZE + SQUARE_SIZE // 3
        cv2.putText(board, label, (x, BOARD_SIZE + 30), FONT, FONT_SCALE, TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)

    return board


# Overlay pieces based on the chessboard matrix
def add_pieces_from_matrix(board, board_matrix):
    for row in range(8):
        for col in range(8):
            piece = board_matrix[row][col]
            if piece:
                color, piece_type = piece[0], piece[1] # "wP" -> "w", "P" 
                piece_image_path = f"{PIECES_FOLDER}{color}{piece_type}.png"
                piece_image = cv2.imread(piece_image_path, cv2.IMREAD_UNCHANGED)
                if piece_image is not None:
                    piece_image = cv2.resize(piece_image, (SQUARE_SIZE, SQUARE_SIZE))
                    overlay_image(board, piece_image, (col + 1) * SQUARE_SIZE, row * SQUARE_SIZE)


# Overlay an image with transparency
def overlay_image(board, piece_image, x, y):
    bgr, alpha = piece_image[:, :, :3], piece_image[:, :, 3]
    for c in range(3):  # Apply to BGR channels
        board[y:y + SQUARE_SIZE, x:x + SQUARE_SIZE, c] = \
            board[y:y + SQUARE_SIZE, x:x + SQUARE_SIZE, c] * (1 - alpha / 255.0) + bgr[:, :, c] * (alpha / 255.0)


# Visualize chessboard matrix
def visualize_chessboard_with_labels(board_matrix):
    global board
    board = draw_chessboard_with_labels()
    add_pieces_from_matrix(board, board_matrix)
    cv2.imshow("Chessboard Visualization", board)


# --------------------------------- MOVE VALIDATION FUNCTIONS ---------------------------------


# Function to validate a move
def is_valid_move(board_matrix, start, end, player_color):
    # Get the piece being moved
    piece = get_piece_at_square(board_matrix, start)   

    # Check if there is a piece at the start and it matches the player's color
    if not piece or piece[0] != player_color:
        #print("No your piece at the starting square.")
        return False

    # Extract piece type (e.g., "P" for pawn)
    piece_type = piece[1]

    # Check if target is occupied by the player's piece
    target_piece = get_piece_at_square(board_matrix, end)
    if target_piece and target_piece[0] == player_color:
        #print("You cannot capture your own piece.")
        return False

    # Validate moves based on piece type
    if piece_type == "P":  # Pawn
        return validate_pawn_move(board_matrix, start, end, player_color)
    elif piece_type == "R":  # Rook
        return validate_rook_move(board_matrix, start, end)
    elif piece_type == "N":  # Knight
        return validate_knight_move(start, end)
    elif piece_type == "B":  # Bishop
        return validate_bishop_move(board_matrix, start, end)
    elif piece_type == "Q":  # Queen
        return validate_queen_move(board_matrix, start, end)
    elif piece_type == "K":  # King
        return validate_king_move(board_matrix, start, end, player_color)
    else:
        print("Invalid piece type.")
        return False


# Function to validate pawn moves
def validate_pawn_move(board_matrix, start, end, player_color):
    start_row, start_col = position_to_indices(start)
    end_row, end_col = position_to_indices(end)

    direction = -1 if player_color == "w" else 1

    # Normal move (one step forward)
    if start_col == end_col and end_row == start_row + direction:
        return not board_matrix[end_row][end_col]

    # Double move (initial move)
    if start_col == end_col and end_row == start_row + 2 * direction:
        if (player_color == "w" and start_row == 6) or (player_color == "b" and start_row == 1):
            return not board_matrix[end_row][end_col] and not board_matrix[start_row + direction][start_col]

    # Capture move (diagonal)
    if abs(end_col - start_col) == 1 and end_row == start_row + direction:
        if board_matrix[end_row][end_col] and board_matrix[end_row][end_col][0] != player_color:
            return True
        
        # En passant capture
        if en_passant_possibility_flag == True:
            return validate_en_passant(board_matrix, start, end)

    return False


# Function to validate rook moves
def validate_rook_move(board_matrix, start, end):
    start_row, start_col = position_to_indices(start)
    end_row, end_col = position_to_indices(end)

    if start_row != end_row and start_col != end_col:
        return False

    if start_row == end_row:  # Horizontal
        step = 1 if end_col > start_col else -1
        for col in range(start_col + step, end_col, step):
            if board_matrix[start_row][col]:
                return False
    else:  # Vertical
        step = 1 if end_row > start_row else -1
        for row in range(start_row + step, end_row, step):
            if board_matrix[row][start_col]:
                return False

    return True


# Function to validate knight moves
def validate_knight_move(start, end):
    start_row, start_col = position_to_indices(start)
    end_row, end_col = position_to_indices(end)

    row_diff = abs(end_row - start_row)
    col_diff = abs(end_col - start_col)
    return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)


# Function to validate bishop moves
def validate_bishop_move(board_matrix, start, end):
    start_row, start_col = position_to_indices(start)
    end_row, end_col = position_to_indices(end)

    if abs(end_row - start_row) != abs(end_col - start_col):
        return False

    row_step = 1 if end_row > start_row else -1
    col_step = 1 if end_col > start_col else -1
    for i in range(1, abs(end_row - start_row)):
        if board_matrix[start_row + i * row_step][start_col + i * col_step]:
            return False

    return True


# Function to validate queen moves
def validate_queen_move(board_matrix, start, end):
    # Queen combines rook and bishop movement
    return validate_rook_move(board_matrix, start, end) or validate_bishop_move(board_matrix, start, end)


# Function to validate king moves
def validate_king_move(board_matrix, start, end, player_color):
    start_row, start_col = position_to_indices(start)
    end_row, end_col = position_to_indices(end)
    
    if max(abs(end_row - start_row), abs(end_col - start_col)) == 1:
        return True
    
    if castling_possibility_flag:
        # Castling logic
        if abs(end_col - start_col) == 2:
        
            if player_color == "w" and start == "E1":  # White King starting square
                if end == "G1":  # Kingside castling
                    return validate_castling(board_matrix, player_color, "wR2")
                if end == "C1":  # Queenside castling
                    return validate_castling(board_matrix, player_color, "wR1")

            if player_color == "b" and start == "E8":  # Black King starting square
                if end == "G8":  # Kingside castling
                    return validate_castling(board_matrix, player_color, "bR2")
                if end == "C8":  # Queenside castling
                    return validate_castling(board_matrix, player_color, "bR1")
        
    return False
    
    
    
# Check for pawn promotion
def pawn_promotion(board_matrix, end):
    # Get the piece at end square
    piece = get_piece_at_square(board_matrix, end)
        
    # Extract player color and piece type (e.g., "w" for white and "P" for pawn)
    player_color, piece_type = piece[0], piece[1]
    
    if piece_type == "P":
        end_row, end_col = position_to_indices(end)
        if (player_color == "w" and end_row == 0) or (player_color == "b" and end_row == 7):
            print("Pawn promotion!")
            promotion_choice = None
            while promotion_choice not in ["Q", "R", "B", "N"]:
                promotion_choice = input("Choose a piece for promotion (Q for Queen, R for Rook, B for Bishop, N for Knight): ").upper().strip()
                if promotion_choice not in ["Q", "R", "B", "N"]:
                    print("Invalid choice. Please choose again.")
            board_matrix[end_row][end_col] = player_color + promotion_choice
            print(f"Pawn promoted to {promotion_choice} at {end}.\n")
            return True

    return False


# Function to validate en_passant
def validate_en_passant(board_matrix, start, end):
    global en_passant_flag

    start_row, start_col = position_to_indices(start)
    end_row, end_col = position_to_indices(end)
    
    if last_move:
        last_start, last_end = last_move
        last_piece = get_piece_at_square(board_matrix, last_end)
        last_piece_type = last_piece[1]
        
        last_start_row, last_start_col = position_to_indices(last_start)
        last_end_row, last_end_col = position_to_indices(last_end)
    
        # Check if last move was a double pawn move
        if last_piece_type == "P" and abs(last_start_row - last_end_row) == 2 and last_end_col == end_col:
            # Ensure the opponent's pawn is adjacent to the current pawn
            if board_matrix[last_end_row][last_end_col] and last_end_row == start_row:
                en_passant_flag = True
                return True
    
    return False
    
    
# Function to validate castling
def validate_castling(board_matrix, player_color, rook_id):
    global castling_flag

    if piece_movement_status[player_color + "K"] or piece_movement_status[rook_id]:
        return False  # King or rook has already moved
        
    row = 7 if player_color == "w" else 0
    if rook_id[-1] == "1":  # Queenside castling
        if any(board_matrix[row][col] for col in range(1, 4)):  # Check if squares are empty
            return False
        if any(is_square_under_attack(board_matrix, indices_to_position(row, col), player_color) for col in range(2, 5)):
            return False  # King cannot move through or into check
    else:  # Kingside castling
        if any(board_matrix[row][col] for col in range(5, 7)):  # Check if squares are empty
            print (board_matrix[row][col])
            return False
        if any(is_square_under_attack(board_matrix, indices_to_position(row, col), player_color) for col in range(4, 7)):
            return False  # King cannot move through or into check

    castling_flag = True
    
    return True


# Function to check if a piece is under attack
def is_square_under_attack(board_matrix, square, player_color):
    opponent_color = "b" if player_color == "w" else "w"

    # Iterate through all squares on the board
    for row in range(8):
        for col in range(8):
            piece = board_matrix[row][col]
            # Check if the piece belongs to the opponent
            if piece and piece[0] == opponent_color:
                opponent_piece_square = indices_to_position(row, col)
                # Validate if the piece can move to the target square
                if is_valid_move(board_matrix, opponent_piece_square, square, opponent_color):
                    return True

    return False
    
    
# --------------------------------- CHECKMATE CHECK FUNCTIONS ---------------------------------

# Other end game conditions like clock, draw by stalemate, fifty-move rule and threefold repetition are not included!


# Locate the King's square
def find_king_square(board_matrix, king_color):
    for row in range(8):
        for col in range(8):
            piece = board_matrix[row][col]
            if piece == f"{king_color}K":
                return indices_to_position(row, col)
    return None


# Check if the King is in check
def is_king_in_check(board_matrix, king_color):
    king_square = find_king_square(board_matrix, king_color)
    return is_square_under_attack(board_matrix, king_square, king_color)


# Check if the player has any legal moves
def has_legal_moves(board_matrix, king_color):
    for row in range(8):
        for col in range(8):
            piece = board_matrix[row][col]
            if piece and piece[0] == king_color:
                piece_square = indices_to_position(row, col)
                for target_row in range(8):
                    for target_col in range(8):
                        target_square = indices_to_position(target_row, target_col)
                        if is_valid_move(board_matrix, piece_square, target_square, king_color):
                            # Temporarily make the move to check if it resolves the check
                            # Unfortunately, as it is now, en passant move is not checked if it resolves the check
                            temp_board = [row[:] for row in board_matrix]
                            temp_board[target_row][target_col] = piece
                            temp_board[row][col] = None
                            if not is_king_in_check(temp_board, king_color):
                                return True
    return False


# Check for checkmate
def is_checkmate(board_matrix, king_color):
    if is_king_in_check(board_matrix, king_color) and not has_legal_moves(board_matrix, king_color):
        return True
    return False


# --------------------------------- VARIABLE DEFINITIONS ---------------------------------


# Define chessboard grid dimensions and size for the warped chessboard
chessboard_size=8 # 8x8 chessboard
grid_width=100
grid_height=100
chessboard_width = chessboard_size * grid_width
chessboard_height = chessboard_size * grid_height


# Constants for chessboard matrix visualization
BOARD_SIZE = 400  # Chessboard size in pixels
SQUARE_SIZE = BOARD_SIZE // 8  # Each square's size
PIECES_FOLDER = "pieces/"  # Folder with PNG images of chess pieces
FONT = cv2.FONT_HERSHEY_SIMPLEX  # Font for labels
FONT_SCALE = 0.6  # Size of the font
FONT_THICKNESS = 1  # Thickness of the font
TEXT_COLOR = (0, 0, 0)  # Black text color


# Initialize a dictionary to store squares and their centers
squares_centers = {}

# Map chessboard squares to grid coordinates
for row in range(chessboard_size):
    for col in range(chessboard_size):
        # Calculate the center of the current rectangle
        center_x = col * grid_width + grid_width // 2
        center_y = row * grid_height + grid_height // 2
        center = (center_x, center_y)
        
        # Map to chessboard notation
        column_letter = chr(ord('A') + col) # 'A' for col=0, 'B' for col=1, etc.
        row_number = chessboard_size - row  # Reverse row order (1 at the bottom, 8 at the top)
        square = f"{column_letter}{row_number}"
        
        # Store the chessboard square and its center coordinates in the dictionary
        squares_centers[square] = center

    
# Define variables indicating whose turn it is
white_to_move = True
current_turn_color = "w"
opponent_color = "b"

# Dictionary to store dynamic variables (used in connected components where the number varies depending on the move)
dynamic_vars = {}


# List to store pieces involved in a move
involved_pieces = []


# Special move flags
global en_passant_possibility_flag, en_passant_flag, castling_possibility_flag, castling_flag

# Define piece list for special moves
en_passant_piece_list = ["wP", "bP", None]
wR1_castling_piece_list = ["wK", "wR1", None, None]
wR2_castling_piece_list = ["wK", "wR2", None, None]
bR1_castling_piece_list = ["bK", "bR1", None, None]
bR2_castling_piece_list = ["bK", "bR2", None, None]

# Track last move (for en passant)
global last_move
last_move = None

# Keep pieces movement status (for castling)
piece_movement_status = {
    "wK": False,  # White King
    "wR1": False,  # White Rook (Queenside)
    "wR2": False,  # White Rook (Kingside)
    "bK": False,  # Black King
    "bR1": False,  # Black Rook (Queenside)
    "bR2": False,  # Black Rook (Kingside)
}


# Set up calibration window with trackbard for Canny thresholds
cv2.namedWindow("calibration")
cv2.createTrackbar('lowThreshold',"calibration",200,255,nothing)
cv2.createTrackbar('highThreshold',"calibration",230,255,nothing)


# Capture video input from camera
cap = cv2.VideoCapture(1)


# Define the various phases of the system
phases = ["Chessboard Calibration",
          "Piece Initialization",
          "Game In Progress",
          "End Game"]

# Define a phase iterator
phase_iter = iter(phases)


# Directory to save the game boards
output_folder = os.path.join(os.path.dirname(__file__), 'game')


# --------------------------------- MAIN EXECUTION ---------------------------------


# Iter to the first phase
phase = next(phase_iter)


while(True):
    # Constantly display webcam feed
    ret, frame = cap.read()
    cv2.imshow('webcam',frame) 
    
    
    # Chessboard Calibration phase - Calibrate the canny thresholds so that the border of the chessboard is detected and warped in an chessboard_width x chessboard_height image
    while(phase == phases[0]):
        # Constantly display webcam feed
        ret, frame = cap.read() 
        cv2.imshow('webcam',frame) 
        
        
        # Grayscale conversion
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
        
        # Apply median blur to reduce noise
        blurred = cv2.medianBlur(gray, 5)         
        '''
        # Apply Gausian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        '''
        
        # Get trackbar values for thresholds
        lowThreshold = cv2.getTrackbarPos('lowThreshold',"calibration")
        highThreshold = cv2.getTrackbarPos('highThreshold',"calibration")
        
        # Use Canny edge detection to detect edges 
        canny = cv2.Canny(blurred, lowThreshold, highThreshold) 
        
        # Apply dilation to thicken the edges and help with line detection
        dilated = cv2.dilate(canny, None, iterations=2)
        
        # Identify connected components
        ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dilated)
        
        # Find the largest non-black component
        largest_component_index = np.argsort(stats[0:, cv2.CC_STAT_AREA])[-2]
        
        # Mask the largest component
        largest_component_mask = (labels == largest_component_index).astype(np.uint8) * 255
        
        # Get bounding box and area of largest component
        x, y, w, h, area = stats[largest_component_index]
        top_left = (x, y) 
        top_right = (x + w, y)
        bottom_left = (x, y + h)
        bottom_right = (x + w, y + h)
        
        # Create copies
        temp = frame.copy()
        gray_temp = gray.copy()
        
        # Draw bounding box on the frame
        cv2.rectangle(gray_temp, top_left, bottom_right, 255, 2)
        
        # Perspective transformation of detected chessboard to normalized 800*800 assuming that camera is aligned on top of the chessboard and to the right of the white player
        pts1 = np.float32([top_right,bottom_right,top_left,bottom_left]) # start points for perspective transformation
        pts2 = np.float32([[0,0],[chessboard_width,0],[0,chessboard_height],[chessboard_width,chessboard_height]]) # Target points for perspective transformation
        M = cv2.getPerspectiveTransform(pts1,pts2) # Compute perspective transformation matrix
        dst = cv2.warpPerspective(temp,M,(chessboard_width,chessboard_height)) # Applying 

        
        # Stack canny, dilated, largest_component_mask and gray_temp
        result = np.hstack((
        cv2.resize(canny, None, fx=0.4, fy=0.4, interpolation=cv2.INTER_AREA),
        cv2.resize(dilated, None, fx=0.4, fy=0.4, interpolation=cv2.INTER_AREA),
        cv2.resize(largest_component_mask, None, fx=0.4, fy=0.4, interpolation=cv2.INTER_AREA),
        cv2.resize(gray_temp, None, fx=0.4, fy=0.4, interpolation=cv2.INTER_AREA)
        ))
        
        
        # Display calibration result
        cv2.imshow("calibration",result)        
        # Display the detected chessboard
        cv2.imshow('chessboard',dst)
        
        
        # When chessboard is calibrated press SPACE to move to the next phase
        k = cv2.waitKey(1) & 0xFF
        if k == 32: # Press the SPACE key
            phase = next(phase_iter) # Move to next phase 
            
            print("Set up chessboard with initial piece positions. Press SPACE when ready to start the game.\n")
            
            cv2.destroyWindow('calibration') # Close the calibration window
            
            break

   
    # Piece Initialization phase - Setting up chessboard with initial positions of pieces and alligning them with the marked centers on the warped image
    while(phase == phases[1]):
        # Constantly display webcam feed
        ret, frame = cap.read()
        cv2.imshow('webcam',frame)

        
        # Warp
        dst = cv2.warpPerspective(frame,M,(chessboard_size * grid_width,chessboard_size * grid_height))
        
        # Copy for snapshot without the centers and the square anotations
        dst_snapshot = dst.copy()
                
        # Paint centers and square anotations in the warped image
        dst = paint_centers_and_squares(dst, squares_centers)

        # Display chessboard with red centers and square anotations
        cv2.imshow('chessboard',dst) 
        
        
        # When all chess pieces are on the chessboard and alligned with the centers in the image press SPACE to move to the next phase
        k = cv2.waitKey(1) & 0xFF
        if k == 32: # Press SPACE key to start game
            phase = next(phase_iter) # Move to next phase
            
            print("Game started\n")
            print("White to move")
            
            # Initialize chessboard matrix
            chessboard = initialize_chessboard()
            # Visualize chessboard matrix
            visualize_chessboard_with_labels(chessboard)
            # Array to track game boards as the game progresses
            game_boards = [board]
            
            # Capture initial positions snapshot
            previous_snapshot = cv2.cvtColor(dst_snapshot, cv2.COLOR_BGR2GRAY)
            
            break
    
    # Game In Progress phase - Capturing moves, validating moves and updating the board
    while(phase == phases[2]):
        # Constantly display webcam feed
        ret, frame = cap.read()
        cv2.imshow('webcam',frame)

    
        # Warp
        dst = cv2.warpPerspective(frame,M,(chessboard_size * grid_width,chessboard_size * grid_height))
        
        # Copy for snapshot without the centers and the squares
        dst_snapshot = dst.copy()
        
        # Paint centers and annotate squares in the warped image
        dst = paint_centers_and_squares(dst, squares_centers)
        
        
        # Display chessboard with red centers and annotated squares
        cv2.imshow('chessboard',dst) 
        
        
        # - When the player has finished his move, press SPACE to track the move, validate the move, check for checkmate and update the chessboard matrix.
        # - Press R in order to reset the previous snapshot in case some pieces have been moved by mistake and as a result the diff image does not correspond to the move.
        # - Press D in order to end the game as a draw.
        # - Press Q in order to resign.
        k = cv2.waitKey(1) & 0xFF
            
        if k == 32: # Press SPACE key to process move
            # Capture current snapshot
            current_snapshot = cv2.cvtColor(dst_snapshot, cv2.COLOR_BGR2GRAY)
            
            # Compute frame difference by subtracting previous from current snapshot
            diff = current_snapshot - previous_snapshot
            
            # Band threshold on subtraction to highlight changes 
            thresholded_image = cv2.inRange(diff, 20, 225)
            
            # Erode to remove noise
            eroded = cv2.erode(thresholded_image, None, iterations=4)
            
            # Apply more rounds of dilation to emphasize
            dilated = cv2.dilate(eroded, None, iterations=12)
            
            '''
            # Display image subtraction
            show_image_with_waitkey(diff)
            # Display subtraction result after band thresholding
            show_image_with_waitkey(thresholded_image)
            '''
            # Display band thresholding result after erosion and dilation
            #show_image_with_waitkey(dilated)
            
            
            # Identify connected components
            ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dilated)

            
            # Reset special move flags
            en_passant_possibility_flag = False
            en_passant_flag = False
            castling_possibility_flag = False
            castling_flag = False
            
            # Only 1 component, the background
            if ret == 1:
                print("Make a move before pressing SPACE.")
                break
            # Only 1 non-black component, no move corresponds
            elif ret == 2:
                print("Only 1 change detected. Reset board and play again.")
                break
            # 2 non-black components, simple move
            elif ret == 3:
                pass
            # 3 non-black components, special move en passant
            elif ret == 4:
                en_passant_possibility_flag = True
            # 4 non-black components, special move castling
            elif ret == 5:
                castling_possibility_flag = True
            # 5 or more non-black components, no move corresponds
            else:
                print("Too many changes detected. Reset board and play again.")
                break
            
            # Reset dynamic vars dictionary
            dynamic_vars.clear()
            # Reset square_not_found_flag
            square_not_found_flag = False
            # Reset involved pieces list
            involved_pieces.clear()
            
            # For number of components found (start from 2nd as 1st is background)
            for i in range(1, ret):
                # Find the non-black components
                dynamic_vars[f"largest_component_index_{i}"] = np.argsort(stats[0:, cv2.CC_STAT_AREA])[-i-1]
                           
                # Mask the non-black components
                dynamic_vars[f"largest_component_mask_{i}"] = (labels == dynamic_vars[f"largest_component_index_{i}"]).astype(np.uint8) * 255
                        
                # Detect the squares corresponding to the masks
                for square, center in squares_centers.items():
                    dynamic_vars[f"square{i}"] = None
                    if is_point_in_mask(dynamic_vars[f"largest_component_mask_{i}"], center):
                        dynamic_vars[f"square{i}"] = square
                        break
                
                # If mask is not overlaping with a square center
                if dynamic_vars[f"square{i}"] is None:
                    square_not_found_flag = True
                    break
            
                # Get the pieces corresponding to the squares
                dynamic_vars[f"piece{i}"] = get_piece_at_square(chessboard, dynamic_vars[f"square{i}"])
                
                # Append piece in the involved pieces list
                involved_pieces.append(dynamic_vars[f"piece{i}"])
                
                # Determine moving piece, start square and end square
                # For simple moves
                if not en_passant_possibility_flag and not castling_possibility_flag:
                
                    if dynamic_vars[f"piece{i}"] is not None and dynamic_vars[f"piece{i}"][0] == current_turn_color:
                        moving_piece = dynamic_vars[f"piece{i}"]
                        start_square = dynamic_vars[f"square{i}"]
                    else:
                        end_square = dynamic_vars[f"square{i}"]
                        
                # For en passant
                elif en_passant_possibility_flag:
                    if dynamic_vars[f"piece{i}"] is not None and dynamic_vars[f"piece{i}"][0] == current_turn_color:
                        moving_piece = dynamic_vars[f"piece{i}"]
                        start_square = dynamic_vars[f"square{i}"]
                    elif dynamic_vars[f"piece{i}"] is None:
                        end_square = dynamic_vars[f"square{i}"]
            
                # For castling (need all the pieces to validate the castling positions)
                elif castling_possibility_flag:
                    pass
                        
            
            
            # If any mask is not overlaping with a square center
            if square_not_found_flag:
                print("Some mask does not overlap with any square center. Reset board and play again.")
                break
                
            # If 3 changes are detected make sure the pieces are valid for en passant
            if en_passant_possibility_flag:
                if Counter(involved_pieces) != Counter(en_passant_piece_list):
                    print("3 changes were detected but their positions do not correspond to valid en passant pieces. Reset board and play again.")
                    break
            
            # If 4 changes are detected make sure the pieces are valid for castling and detect start and and position of King
            if castling_possibility_flag:
                if Counter(involved_pieces) == Counter(wR1_castling_piece_list):
                    moving_piece = "wK"
                    start_square = "E1"
                    end_square = "C1"
                    #rook_id = "wR1"
                elif Counter(involved_pieces) == Counter(wR2_castling_piece_list):
                    moving_piece = "wK"
                    start_square = "E1"
                    end_square = "G1"
                    #rook_id = "wR2"
                elif Counter(involved_pieces) == Counter(bR1_castling_piece_list):
                    moving_piece = "bK"
                    start_square = "E8"
                    end_square = "C8"
                    #rook_id = "bR1"
                elif Counter(involved_pieces) == Counter(bR2_castling_piece_list):
                    moving_piece = "bK"
                    start_square = "E8"
                    end_square = "G8"
                    #rook_id = "bR1"
                else:
                    print("4 changes were detected but their squares do not correspond to valid castling pieces. Reset board and play again.")
                    break
                    

            # Check whether the move is valid
            if is_valid_move(chessboard, start_square, end_square, current_turn_color) and en_passant_possibility_flag == en_passant_flag and castling_possibility_flag == castling_flag:
                # Create a copy of the chessboard matrix
                chessboard_bk = copy.deepcopy(chessboard)
            
                # Update the chessboard matrix
                move_piece(chessboard, start_square, end_square)
                
                # Remove the opponent's Pawn that was captured en passant
                if en_passant_flag:
                    last_start, last_end = last_move
                    last_end_row, last_end_col = position_to_indices(last_end)
                
                    chessboard[last_end_row][last_end_col] = None
                
                # Move the Rook based on King's end square              
                if castling_flag:
                    start_row, start_col = position_to_indices(start_square)
                    end_row, end_col = position_to_indices(end_square)
                
                    if end_col == 6:  # Kingside castling
                        rook_start = (start_row, 7)
                        rook_end = (start_row, 5)
                    else:  # Queenside castling
                        rook_start = (start_row, 0)
                        rook_end = (start_row, 3)
                        
                    # Move the Rook
                    chessboard[rook_end[0]][rook_end[1]] = chessboard[rook_start[0]][rook_start[1]]
                    chessboard[rook_start[0]][rook_start[1]] = None
                
                # Check whether your King is in check
                if is_king_in_check(chessboard, current_turn_color):
                    print("King in check. Reset board and play again.")
                    
                    # Revert the chessboard matricx before the move
                    chessboard = copy.deepcopy(chessboard_bk)
                    
                    break
                
                # Move was successful
                print(f"Moved {moving_piece} from {start_square} to {end_square}\n")
                
                
                # Check for Pawn promotion
                if pawn_promotion(chessboard, end_square):
                    # Need to recapture current snapshot with promoted Pawn
                    ret, frame = cap.read()
                    
                    # Warp
                    dst_snapshot = cv2.warpPerspective(frame,M,(chessboard_size * grid_width,chessboard_size * grid_height))
                    
                    # Capture current snapshot
                    current_snapshot = cv2.cvtColor(dst_snapshot, cv2.COLOR_BGR2GRAY)
                
                # Visualize chessboard matrix
                visualize_chessboard_with_labels(chessboard)
                
                # Append new board in array to track game boards
                game_boards.append(board)
                
            
                # Check if there is a checkmate
                if is_checkmate(chessboard, opponent_color):
                    print(f"Checkmate! {current_turn_color.upper()} wins!\n")
                    
                    phase = next(phase_iter) # Move to next phase
                    
                    break
                
                # Update last move
                last_move = (start_square, end_square)
                
                # Update castling pieces movement status
                if moving_piece in piece_movement_status.keys():
                    piece_movement_status[moving_piece] = True
                
                # Update snapshot for next move detection
                previous_snapshot = current_snapshot
                
                # Update turn variables
                white_to_move = not(white_to_move)               
                if white_to_move:
                    current_turn_color = 'w'
                    opponent_color = 'b'
                else:
                    current_turn_color = 'b'
                    opponent_color = 'w'
                    
            # In case move is not valid        
            else:
                print("Invalid move. Reset board and play again.")
                break
            
            # Indicate turn
            if white_to_move:
                print("White to move.")
            else:
                print("Black to move.")


        if k == ord('r'): # Press R key to reset the previous snapshot
            # Capture current positions snapshot
            previous_snapshot = cv2.cvtColor(dst_snapshot, cv2.COLOR_BGR2GRAY)
            
            
        if k == ord('d'): # Press D key in case of draw
            print(f"Draw!\n")
                    
            phase = next(phase_iter) # Move to next phase
                    
            break
            
            
        if k == ord('q'): # Press Q key in case of resign
            print(f"{current_turn_color.upper()} Resigned! {opponent_color.upper()} wins!\n")
                    
            phase = next(phase_iter) # Move to next phase
                    
            break
            
            
    # End Game phase - User has the option to save the game boards or simply exit the app
    if phase == phases[3]:
        cv2.destroyWindow("chessboard")
        cv2.destroyWindow("webcam")
    
        print("Press 'S' to save game. Otherwise, press 'Esc' to exit.")
        
        k = cv2.waitKey(0) & 0xFF
        
        if k == ord('s'): # Press S key to save the game boards
            # Ensure the output folder exists
            os.makedirs(output_folder, exist_ok=True)
            
            # Save each board
            for idx, image in enumerate(game_boards):
                filename = os.path.join(output_folder, f"board_{idx + 1}.png")
                cv2.imwrite(filename, image)
                print(f"Saved {filename}")
                
            break
            
        if k == 27: # Press Esc key to exit
            break


# Stop video camera feed        
cap.release()
# Destroy all windows
cv2.destroyAllWindows()
