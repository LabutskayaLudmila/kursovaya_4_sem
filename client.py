import os
import socket
import tkinter as tk
from tkinter import messagebox
import threading

player = ''
concurrent_player = 'X'


def connect_to_server():
    try:
        global host, port, s
        host = "192.168.50.106"  # IP-адрес сервера
        port = 8888  # Порт сервера
        s = socket.socket()
        s.connect((host, port))

        while True:
            response = s.recv(1024).decode()
            if not response:
                break
            global player
            player = response

            start_data_thread()
            break

    except socket.error as msg:
        print("Ошибка при подключении к серверу: " + str(msg))


def send_data(button):
    try:
        message = str(button.row) + ',' + str(button.col)  # Преобразуем координаты кнопки в строку
        s.send(str.encode(message))

    except socket.error as msg:
        print("Ошибка при отправке данных: " + str(msg))


def start_data_thread():
    server_thread = threading.Thread(target=get_data)
    server_thread.daemon = True
    server_thread.start()


def get_data():
    try:
        while True:
            response = s.recv(1024).decode()
            if not response:
                Exception("Нет ответа от сервера")

            data = response.split(',')

            result = data[0]  # принимает информацию о состоянии игры
            board_state = data[1:]  # принимает состояние доски

            if result == "valid":
                change_player()
                # Обновление игрового поля на основе полученного состояния
                if concurrent_player == player:
                    update_board(board_state)
                else:
                    update_board_other_player_move(board_state)
            elif result == "invalid":
                messagebox.showerror("Недопустимый ход", "Это поле уже занято. Выберите другое поле.")
            elif result[:7] == "Победил":
                update_board_other_player_move(board_state)
                messagebox.showinfo("Игра завершена", result)
                reset_game()
            elif result == "draw":
                update_board_other_player_move(board_state)
                messagebox.showinfo("Игра завершена", "Ничья!")
                reset_game()

    except Exception as e:
        print(e)
        s.close()
        os.abort()


def update_board(board_state):
    for i, row in enumerate(board_state):
        for j, value in enumerate(row):
            button = buttons[i][j]
            button['text'] = value
            button['state'] = 'disabled' if value != ' ' else 'normal'


def update_board_other_player_move(board_state):
    for i, row in enumerate(board_state):
        for j, value in enumerate(row):
            button = buttons[i][j]
            button['text'] = value
            button['state'] = 'disabled'


def reset_game():
    global concurrent_player
    concurrent_player = 'X'
    s.send('restart'.encode())
    for row in buttons:
        for button in row:
            button['text'] = ' '
            button['state'] = 'normal'


def handle_button_click(button):
    if player == concurrent_player:
        if button['text'] == ' ':
            send_data(button)


def change_player():
    global concurrent_player
    concurrent_player = 'O' if concurrent_player == 'X' else 'X'


def main():
    connect_to_server()

    # Создаем графическое окно игры
    window = tk.Tk()
    window.title("Игрок " + player)

    def on_closing():
        window.destroy()
        s.send('close'.encode())

    window.protocol("WM_DELETE_WINDOW", on_closing)

    # Создаем кнопки для игрового поля
    global buttons

    buttons = []
    for i in range(3):
        row = []
        for j in range(3):
            button = tk.Button(window, text=' ', width=10, height=5)
            button.row = i  # Добавляем атрибуты row и col для хранения координат кнопки
            button.col = j
            button.configure(
                command=lambda b=button: handle_button_click(b))  # Передаем кнопку в функцию handle_button_click
            button.grid(row=i, column=j)

            if concurrent_player != player:
                button.config(state='disabled')

            row.append(button)
        buttons.append(row)

    # Запускаем главный цикл событий
    window.mainloop()


if __name__ == "__main__":
    main()
