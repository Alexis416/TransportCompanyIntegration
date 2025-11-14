import tkinter as tk
from tkinter import ttk
import sqlite3

class Truck:
    def __init__(self, model, capacity, length, width, height):
        self.model = model
        self.capacity = capacity
        self.length = length
        self.width = width
        self.height = height
        self.is_available = True

class TransportManager:
    def __init__(self):
        self.conn = sqlite3.connect('trucks.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS trucks
                         (id INTEGER PRIMARY KEY, model TEXT, capacity REAL, length REAL,
                          width REAL, height REAL, is_available BOOLEAN)''')
        self.conn.commit()

    def add_truck(self, model, capacity, length, width, height):
        self.c.execute("INSERT INTO trucks (model, capacity, length, width, height, is_available) "
                       "VALUES (?, ?, ?, ?, ?, ?)", (model, capacity, length, width, height, True))
        self.conn.commit()

    def remove_truck(self, truck_id):
        self.c.execute("DELETE FROM trucks WHERE id = ?", (truck_id,))
        self.conn.commit()

    def book_truck(self, truck_id, weight, len_gr, wid_gr, hei_gr):
        self.c.execute("SELECT capacity, length, width, height, is_available FROM trucks WHERE id = ?", (truck_id,))
        capacity, length, width, height, is_available = self.c.fetchone()
        if is_available and capacity >= weight and length >= len_gr and width >= wid_gr and height >= hei_gr:
            self.c.execute("UPDATE trucks SET is_available = ? WHERE id = ?", (False, truck_id))
            self.conn.commit()
            return True
        return False

    def release_truck(self, truck_id):
        self.c.execute("UPDATE trucks SET is_available = ? WHERE id = ?", (True, truck_id))
        self.conn.commit()

    def get_all_trucks(self):
        self.c.execute("SELECT id, model, capacity, length, width, height, is_available FROM trucks")
        return self.c.fetchall()

    def get_available_trucks(self, capacity=None, length=None, width=None, height=None):
        if capacity and length and width and height:
            self.c.execute(
                "SELECT id, model, capacity, "
                "length, width, height, is_available FROM trucks WHERE is_available = ? "
                "AND capacity >= ? AND length >= ? AND width >= ? AND height >= ?",
                (True, capacity, length, width, height))
        else:
            self.c.execute("SELECT id, model, capacity, length, width, height, "
                           "is_available FROM trucks WHERE is_available = ?", (True,))
        return self.c.fetchall()

    def get_booked_trucks(self):
        self.c.execute("SELECT id, model, capacity, length, width, height, "
                       "is_available FROM trucks WHERE is_available = ?", (False,))
        return self.c.fetchall()

class TruckManagementApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Управление грузовым транспортом")
        self.geometry("800x600")

        self.transport_manager = TransportManager()

        self.create_widgets()

    def create_widgets(self):
        # Вкладки
        tabs = ttk.Notebook(self)
        tabs.pack(fill="both", expand=True)

        # Вкладка "Добавить/удалить грузовик"
        add_tab = ttk.Frame(tabs)
        tabs.add(add_tab, text="Добавить грузовик")

        add_label = ttk.Label(add_tab, text="Модель:")
        add_label.grid(row=0, column=0, padx=10, pady=10)
        self.add_model_entry = ttk.Entry(add_tab)
        self.add_model_entry.grid(row=0, column=1, padx=10, pady=10)

        add_capacity_label = ttk.Label(add_tab, text="Грузоподъемность (тонн):")
        add_capacity_label.grid(row=1, column=0, padx=10, pady=10)
        add_length_label = ttk.Label(add_tab, text="Длина:")
        add_length_label.grid(row=2, column=0, padx=10, pady=10)
        add_width_label = ttk.Label(add_tab, text="Ширина:")
        add_width_label.grid(row=3, column=0, padx=10, pady=10)
        add_height_label = ttk.Label(add_tab, text="Высота:")
        add_height_label.grid(row=4, column=0, padx=10, pady=10)
        self.add_capacity_entry = ttk.Entry(add_tab)
        self.add_capacity_entry.grid(row=1, column=1, padx=10, pady=10)
        self.add_length_entry = ttk.Entry(add_tab)
        self.add_length_entry.grid(row=2, column=1, padx=10, pady=10)
        self.add_width_entry = ttk.Entry(add_tab)
        self.add_width_entry.grid(row=3, column=1, padx=10, pady=10)
        self.add_height_entry = ttk.Entry(add_tab)
        self.add_height_entry.grid(row=4, column=1, padx=10, pady=10)
        add_button = ttk.Button(add_tab, text="Добавить грузовик", command=self.add_truck)
        add_button.grid(row=5, column=1, padx=10, pady=10)

        # Вкладка "Просмотр транспорта"
        view_tab = ttk.Frame(tabs)
        tabs.add(view_tab, text="Просмотр транспорта")

        all_trucks_label = ttk.Label(view_tab, text="Весь доступный транспорт:")
        all_trucks_label.grid(row=0, column=0, padx=10, pady=10)
        self.all_trucks_listbox = tk.Listbox(view_tab, width=50)
        self.all_trucks_listbox.grid(row=1, column=0, padx=10, pady=10)

        capacity_label = ttk.Label(view_tab, text="Грузоподъемность, тонн (фильтрация):")
        capacity_label.grid(row=0, column=1, padx=10, pady=10)
        self.capacity_entry = ttk.Entry(view_tab)
        self.capacity_entry.grid(row=1, column=1, padx=10, pady=10)

        filter_button = ttk.Button(view_tab, text="Фильтровать по грузоподъемности", command=self.filter_trucks)
        filter_button.grid(row=2, column=0, padx=10, pady=10)

        available_label = ttk.Label(view_tab, text="Свободный транспорт:")
        available_label.grid(row=3, column=0, padx=10, pady=10)
        self.available_trucks_listbox = tk.Listbox(view_tab, width=50)
        self.available_trucks_listbox.grid(row=4, column=0, padx=10, pady=10)

        book_label = ttk.Label(view_tab, text="Вес груза (тонн):")
        book_label.grid(row=3, column=1, padx=10, pady=10)
        self.book_entry = ttk.Entry(view_tab)
        self.book_entry.grid(row=4, column=1, padx=10, pady=10)

        book_length_label = ttk.Label(view_tab, text="Длина груза:")
        book_length_label.grid(row=3, column=2, padx=10, pady=10)
        self.book_length_entry = ttk.Entry(view_tab)
        self.book_length_entry.grid(row=4, column=2, padx=10, pady=10)

        book_width_label = ttk.Label(view_tab, text="Ширина груза:")
        book_width_label.grid(row=3, column=3, padx=10, pady=10)
        self.book_width_entry = ttk.Entry(view_tab)
        self.book_width_entry.grid(row=4, column=3, padx=10, pady=10)

        book_height_label = ttk.Label(view_tab, text="Высота груза:")
        book_height_label.grid(row=3, column=4, padx=10, pady=10)
        self.book_height_entry = ttk.Entry(view_tab)
        self.book_height_entry.grid(row=4, column=4, padx=10, pady=10)

        book_button = ttk.Button(view_tab, text="Забронировать транспорт", command=self.book_truck)
        book_button.grid(row=5, column=1, padx=10, pady=10)

        remove_button = ttk.Button(view_tab, text="Удалить грузовик", command=self.remove_truck)
        remove_button.grid(row=1, column=2, padx=10, pady=10)

        # Вкладка "Занятый транспорт"
        booked_tab = ttk.Frame(tabs)
        tabs.add(booked_tab, text="Занятый транспорт")

        booked_trucks_label = ttk.Label(booked_tab, text="Занятый транспорт:")
        booked_trucks_label.grid(row=0, column=0, padx=10, pady=10)
        self.booked_trucks_listbox = tk.Listbox(booked_tab, width=50)
        self.booked_trucks_listbox.grid(row=1, column=0, padx=10, pady=10)

        realise_button = ttk.Button(booked_tab, text="Отменить бронирование", command=self.release_truck)
        realise_button.grid(row=5, column=0, padx=10, pady=10)

        self.update_all_trucks()
        self.update_available_trucks()
        self.update_booked_trucks()

    def add_truck(self):
        model = self.add_model_entry.get()
        capacity = float(self.add_capacity_entry.get())
        length = float(self.add_length_entry.get())
        width = float(self.add_width_entry.get())
        height = float(self.add_height_entry.get())
        if capacity > 0 and length > 0 and width > 0 and height > 0:
            self.transport_manager.add_truck(model, capacity, length, width, height)
            self.update_all_trucks()
            self.update_available_trucks()
            self.add_model_entry.delete(0, tk.END)
            self.add_capacity_entry.delete(0, tk.END)
            self.add_length_entry.delete(0, tk.END)
            self.add_width_entry.delete(0, tk.END)
            self.add_height_entry.delete(0, tk.END)

    def remove_truck(self):
        selected = self.all_trucks_listbox.curselection()
        if selected:
            truck_id = self.all_trucks_list[selected[0]][0]
            self.transport_manager.remove_truck(truck_id)
            self.update_all_trucks()
            self.update_available_trucks()
            self.update_booked_trucks()

    def filter_trucks(self):
        capacity = float(self.capacity_entry.get())
        if capacity >= 0:
            self.update_all_trucks(capacity)

    def book_truck(self):
        selected = self.available_trucks_listbox.curselection()
        if selected:
            truck_id = self.available_trucks_list[selected[0]][0]
            weight = float(self.book_entry.get())
            length = float(self.book_length_entry.get())
            width = float(self.book_width_entry.get())
            height = float(self.book_height_entry.get())
            if weight > 0 and length > 0 and width > 0 and height > 0:
                if self.transport_manager.book_truck(truck_id, weight, length, width, height):
                    self.update_available_trucks()
                    self.update_booked_trucks()
                    self.book_entry.delete(0, tk.END)
                    self.book_length_entry.delete(0, tk.END)
                    self.book_width_entry.delete(0, tk.END)
                    self.book_height_entry.delete(0, tk.END)
                else:
                    print("Не удалось забронировать грузовик.")

    def release_truck(self):
        selected = self.booked_trucks_listbox.curselection()
        if selected:
            truck_id = self.booked_trucks_list[selected[0]][0]
            self.transport_manager.release_truck(truck_id)
            self.update_available_trucks()
            self.update_booked_trucks()

    def update_all_trucks(self, capacity=None):
        self.all_trucks_list = self.transport_manager.get_all_trucks()
        self.all_trucks_listbox.delete(0, tk.END)
        for truck in self.all_trucks_list:
            if capacity is None or truck[2] >= capacity:
                self.all_trucks_listbox.insert(tk.END, f"{truck[1]} ({truck[2]} тонн, "
                                                    f"Длина {truck[3]}, Ширина {truck[4]}, Высота {truck[5]})")

    def update_available_trucks(self):
        self.available_trucks_list = self.transport_manager.get_available_trucks()
        self.available_trucks_listbox.delete(0, tk.END)
        for truck in self.available_trucks_list:
            self.available_trucks_listbox.insert(tk.END, f"{truck[1]} ({truck[2]} тонн, "
                                                        f"Длина {truck[3]}, Ширина {truck[4]}, Высота {truck[5]})")

    def update_booked_trucks(self):
        self.booked_trucks_list = self.transport_manager.get_booked_trucks()
        self.booked_trucks_listbox.delete(0, tk.END)
        for truck in self.booked_trucks_list:
            self.booked_trucks_listbox.insert(tk.END, f"{truck[1]} ({truck[2]} тонн, "
                                                    f"Длина {truck[3]}, Ширина {truck[4]}, Высота {truck[5]})")

if __name__ == "__main__":
    app = TruckManagementApp()
    app.mainloop()
