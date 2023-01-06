import pygame
import threading
import math
import socket
import sys
import argparse
from piece import Piece, PieceType
from move import Move
from game_state import GameState


TILE_COLOR_A = (100, 100, 100)
TILE_COLOR_B = (180, 180, 180)
TILE_COLOR_MOTION_A = (0, 163, 5)
TILE_COLOR_MOTION_B = (102, 237, 106)
TILE_COLOR_ATTACK_A = (181, 0, 0)
TILE_COLOR_ATTACK_B = (222, 104, 104)

connection = None
am_white = False


def create(args):
    global connection
    global am_white

    listener = socket.socket()
    my_ip = socket.gethostbyname(socket.gethostname())

    with listener:
        listener.bind((my_ip, args.port))
        listener.listen(1)

        print(f"Listening on IP address {my_ip} port {args.port}...")

        connection, addr = listener.accept()
        addr_ip, addr_port = addr

        print(f"Connected to IP {addr_ip} on port {addr_port}")
        am_white = True


def join(args):
    global connection
    global am_white

    connection = socket.socket()
    connection.connect((args.ip, args.port))
    print(f"Connected to IP {args.ip} on port {args.port}")

    am_white = False
    my_turn = False


parser = argparse.ArgumentParser(
    prog="chess",
    description="Play chess with your friends through sockets!",
)

subparsers = parser.add_subparsers()

create_parser = subparsers.add_parser("create")
create_parser.add_argument("port", type=int)
create_parser.set_defaults(func=create)

join_parser = subparsers.add_parser("join")
join_parser.add_argument("ip")
join_parser.add_argument("port", type=int)
join_parser.set_defaults(func=join)

args = parser.parse_args()
args.func(args)


game_state = GameState(am_white)
HEADER_LENGTH = 32


def handle_message(message: bytes):
    move = Move((message[0], message[1]), (message[2], message[3]))

    if game_state.verify_move(move, False):
        game_state.make_move(move)

        if len(message) == 5:
            game_state.promote_pawn(
                PieceType.QUEEN if message[4] == ord("q") else PieceType.HORSE,
                not am_white,
            )

        if game_state.is_in_checkmate(am_white):
            print("You got checkmated!")


def receive_loop():
    try:
        while True:
            header = connection.recv(HEADER_LENGTH)

            if header == b"":
                print("Opponent disconnected!")
                sys.exit()

            message_length = int.from_bytes(header, "big", signed=False)

            message = connection.recv(message_length)

            if message == b"":
                print("Opponent disconnected!")
                sys.exit()

            handle_message(message)

    finally:
        connection.close()


receive_loop_thread = threading.Thread(target=receive_loop)
receive_loop_thread.start()


def get_chessboard_size(parent_surface):
    parent_width, parent_height = parent_surface.get_size()

    return min(parent_width, parent_height)


def get_chessboard_padding(parent_surface, chessboard_size):
    parent_width, parent_height = parent_surface.get_size()

    return (parent_width - chessboard_size) / 2, (parent_height - chessboard_size) / 2


def get_tile_rect(surf, x, y):
    chessboard_size = get_chessboard_size(surf)
    chessboard_padding_x, chessboard_padding_y = get_chessboard_padding(
        surf, chessboard_size
    )

    tile_size = chessboard_size / 8

    return (
        chessboard_padding_x + tile_size * x,
        chessboard_padding_y + tile_size * y,
        tile_size,
        tile_size,
    )


def get_tile_index_by_position(window, position):
    chessboard_size = get_chessboard_size(window)
    chessboard_padding_x, chessboard_padding_y = get_chessboard_padding(
        window, chessboard_size
    )

    tile_size = chessboard_size / 8

    position_x, position_y = position

    tile_index = (
        int((position_x - chessboard_padding_x) // tile_size),
        int((position_y - chessboard_padding_y) // tile_size),
    )

    offset = (
        (position_x - chessboard_padding_x) % tile_size,
        (position_y - chessboard_padding_y) % tile_size,
    )

    return tile_index, offset


piece_atlas = pygame.image.load("pieces.png")
piece_size = 134


def get_piece_image_by_index(x_index, y_index):
    img = pygame.surface.Surface((piece_size, piece_size), pygame.SRCALPHA, 32)

    img.blit(piece_atlas, (-x_index * piece_size, -y_index * piece_size))
    return img


def get_piece_image(piece):
    y_index = 0 if piece.is_white else 1

    match piece.piece_type:
        case PieceType.KING:
            x_index = 0
        case PieceType.QUEEN:
            x_index = 1
        case PieceType.BISHOP:
            x_index = 2
        case PieceType.HORSE:
            x_index = 3
        case PieceType.CASTLE:
            x_index = 4
        case PieceType.PAWN:
            x_index = 5

    return get_piece_image_by_index(x_index, y_index)


holding_index = None
holding_offset = None
possible_motions = set()
possible_attacks = set()


def draw_chessboard(surf):
    for y in range(8):
        for x in range(8):
            if (x + y) % 2 == 0:
                color = TILE_COLOR_A
            else:
                color = TILE_COLOR_B

            if (x, y) in possible_motions:
                if (x + y) % 2 == 0:
                    color = TILE_COLOR_MOTION_A
                else:
                    color = TILE_COLOR_MOTION_B
            elif (x, y) in possible_attacks:
                if (x + y) % 2 == 0:
                    color = TILE_COLOR_ATTACK_A
                else:
                    color = TILE_COLOR_ATTACK_B

            tile_rect = get_tile_rect(surf, x, y)
            pygame.draw.rect(surf, color, tile_rect)

            if game_state.board[y][x] is not None:
                if holding_index == (x, y):
                    continue

                piece_image = get_piece_image(game_state.board[y][x])
                surf.blit(
                    pygame.transform.scale(piece_image, (tile_rect[2], tile_rect[3])),
                    (tile_rect[0], tile_rect[1]),
                )

    if holding_index is not None:
        holding_x, holding_y = holding_index
        offset_x, offset_y = holding_offset

        mouse_x, mouse_y = pygame.mouse.get_pos()
        _, _, width, height = get_tile_rect(surf, holding_x, holding_y)

        piece_image = get_piece_image(game_state.board[holding_y][holding_x])
        scaled_image = pygame.transform.scale(piece_image, (width, height))

        surf.blit(scaled_image, (mouse_x - offset_x, mouse_y - offset_y))


def send_data(data: bytes):
    header_bytes = len(data).to_bytes(HEADER_LENGTH, "big", signed=False)

    connection.send(header_bytes)

    connection.send(data)


promotion_move = None


def make_move(mv: Move):
    global promotion_move

    if game_state.verify_move(mv, True):
        game_state.make_move(mv)

        last_row = 0 if am_white else 7

        dest_x, dest_y = mv.destination

        if (
            dest_y == last_row
            and game_state.board[dest_y][dest_x].piece_type == PieceType.PAWN
        ):
            promotion_move = mv
        else:
            promotion_move = None
            send_data(mv.encode())

            if game_state.is_in_checkmate(not am_white):
                print("Checkmate!")


def get_promotion_button_rects(surf):
    dest_x, dest_y = promotion_move.destination

    if dest_x > 3:
        return pygame.rect.Rect(get_tile_rect(surf, dest_x, dest_y)), pygame.rect.Rect(
            get_tile_rect(surf, dest_x - 1, dest_y)
        )
    else:
        return pygame.rect.Rect(
            get_tile_rect(surf, dest_x + 1, dest_y)
        ), pygame.rect.Rect(get_tile_rect(surf, dest_x, dest_y))


window = pygame.display.set_mode((800, 600))

BUTTON_COLOR = (200, 200, 200)


def blit_image_at_rect(surf, image, rect):
    x, y, width, height = rect

    surf.blit(pygame.transform.scale(image, (width, height)), (x, y))


def promote(chose_queen):
    global promotion_move

    send_data(promotion_move.encode() + (b"q" if chose_queen else b"h"))

    game_state.promote_pawn(
        PieceType.QUEEN if chose_queen else PieceType.HORSE, am_white
    )

    if game_state.is_in_checkmate(not am_white):
        print("Checkmate!")

    promotion_move = None


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            connection.shutdown(socket.SHUT_RDWR)
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if promotion_move is not None:
                queen_rect, horse_rect = get_promotion_button_rects(window)

                if queen_rect.collidepoint(pygame.mouse.get_pos()):
                    promote(True)
                elif horse_rect.collidepoint(pygame.mouse.get_pos()):
                    promote(False)

                continue

                if promotion_move is not None:
                    queen_rect, horse_rect = get_promotion_button_rects(window)

                    if queen_rect.colliderect(pygame.mouse.get_pos()):
                        promote(True)
                    elif horse_rect.colliderect(pygame.mouse.get_pos()):
                        promote(False)

                    continue
            if game_state.my_turn:

                (index_x, index_y), offset = get_tile_index_by_position(
                    window, pygame.mouse.get_pos()
                )

                hovering_piece = game_state.board[index_y][index_x]
                if hovering_piece is not None and hovering_piece.is_white == am_white:
                    holding_index = (index_x, index_y)
                    holding_offset = offset
                    ma = game_state.get_possible_moves(index_x, index_y)
                    possible_attacks = ma.attacks
                    possible_motions = ma.motions

        if event.type == pygame.MOUSEBUTTONUP:
            index, _ = get_tile_index_by_position(window, pygame.mouse.get_pos())

            if index in possible_attacks or index in possible_motions:
                make_move(Move(holding_index, index))

            holding_index = None
            holding_offset = None
            possible_attacks = set()
            possible_motions = set()

    window.fill((200, 200, 200))
    draw_chessboard(window)

    if promotion_move is not None:
        queen_rect, horse_rect = get_promotion_button_rects(window)

        pygame.draw.rect(window, BUTTON_COLOR, queen_rect)
        pygame.draw.rect(window, BUTTON_COLOR, horse_rect)

        queen_image = get_piece_image(Piece(am_white, PieceType.QUEEN))
        horse_image = get_piece_image(Piece(am_white, PieceType.HORSE))

        blit_image_at_rect(window, queen_image, queen_rect)
        blit_image_at_rect(window, horse_image, horse_rect)

    pygame.display.update()
