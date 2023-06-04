import os
import socket
import threading

# Инициализация игрового поля
board = [[' ' for _ in range(3)] for _ in range(3)]
current_player = 'X'  # Текущий игрок
players = ['X', 'O']

clients_sockets = []


def restart():
    global board, current_player
    board = [[' ' for _ in range(3)] for _ in range(3)]
    current_player = 'X'


# здесь получается информация от клиентской части
def handle_client(conn, _):
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break

        if data == 'restart':
            restart()
            continue

        if data == 'close':
            print('Client has been closed')
            print('Aborting server')
            os.abort()
        # Обработка данных от клиента и отправка ответа
        # в data приходит координата нажатой кнопки
        response = process_data(data)

        # отправляем ответ сразу всем клиентам
        for client_socket in clients_sockets:
            client_socket.sendall(response.encode())
    conn.close()


def start_server():
    try:
        host = "192.168.50.106"  # IP-адрес сервера
        port = 8888  # Порт сервера

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen(2)  # Ожидаем не более 2 подключений

        print("Сервер запущен. Ожидание подключений...")

        connected_players = 0  # Счетчик подключенных игроков

        while connected_players < 2:
            conn, addr = s.accept()
            print("Подключение от:", addr)
            clients_sockets.append(conn)

            conn.sendall(players[connected_players].encode())

            # Обработка клиента в отдельном потоке
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()

            connected_players += 1

        print("Все игроки присоединились. Можно начинать играть.")

    except socket.error as msg:
        print("Ошибка при создании сокета: " + str(msg))


def process_data(data):
    global board
    global current_player

    # Распаковка данных о ходе
    row, col = map(int, data.split(','))

    # Проверка допустимости хода
    if board[row][col] == ' ':
        board[row][col] = current_player
        # Проверка на победу
        if check_win(current_player):
            response = "Победил игрок " + current_player
        # Проверка на ничью
        elif check_draw():
            response = "draw"
        else:
            response = "valid"
            # Смена текущего игрока
            current_player = 'O' if current_player == 'X' else 'X'

    else:
        response = "invalid"

    # Формирование ответа
    response += ',' + get_board_state()
    return response


def check_win(player):
    # Проверка по горизонтали и вертикали
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] == player:
            return True
        if board[0][i] == board[1][i] == board[2][i] == player:
            return True

    # Проверка по диагоналям
    if board[0][0] == board[1][1] == board[2][2] == player:
        return True
    if board[0][2] == board[1][1] == board[2][0] == player:
        return True

    return False


def check_draw():
    for row in board:
        if ' ' in row:
            return False
    return True


def get_board_state():
    return ','.join(''.join(row) for row in board)


if __name__ == "__main__":
    start_server()
