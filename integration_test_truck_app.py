import unittest
import sqlite3
from tkinter import Tk

from truck_app import TransportManager, TruckManagementApp


class TestTransportManagerIntegration(unittest.TestCase):
    def setUp(self):
        self.db_path = ':memory:'
        self.transport_manager = TransportManager()
        self.transport_manager.conn = sqlite3.connect(self.db_path)
        self.transport_manager.c = self.transport_manager.conn.cursor()
        self.transport_manager.c.execute('''CREATE TABLE IF NOT EXISTS trucks
                         (id INTEGER PRIMARY KEY, model TEXT, capacity REAL, length REAL,
                          width REAL, height REAL, is_available BOOLEAN)''')
        self.transport_manager.conn.commit()

        self.test_truck_data = {
            'model': 'Volvo FH16',
            'capacity': 20.0,
            'length': 13.6,
            'width': 2.48,
            'height': 2.7
        }

    def tearDown(self):
        if self.transport_manager.conn:
            self.transport_manager.conn.close()

    def test_1_add_and_retrieve_truck_integration(self):
        self.transport_manager.add_truck(
            self.test_truck_data['model'],
            self.test_truck_data['capacity'],
            self.test_truck_data['length'],
            self.test_truck_data['width'],
            self.test_truck_data['height']
        )

        all_trucks = self.transport_manager.get_all_trucks()

        self.assertEqual(len(all_trucks), 1)
        truck = all_trucks[0]
        self.assertEqual(truck[1], self.test_truck_data['model'])
        self.assertEqual(truck[2], self.test_truck_data['capacity'])
        self.assertTrue(truck[6])  # is_available должно быть True

    def test_2_successful_booking_workflow(self):
        self.transport_manager.add_truck(**self.test_truck_data)
        trucks = self.transport_manager.get_all_trucks()
        truck_id = trucks[0][0]

        cargo_params = {
            'weight': 15.0,
            'length': 12.0,
            'width': 2.0,
            'height': 2.0
        }

        booking_result = self.transport_manager.book_truck(
            truck_id,
            cargo_params['weight'],
            cargo_params['length'],
            cargo_params['width'],
            cargo_params['height']
        )

        self.assertTrue(booking_result)

        available_trucks = self.transport_manager.get_available_trucks()
        self.assertEqual(len(available_trucks), 0)

        booked_trucks = self.transport_manager.get_booked_trucks()
        self.assertEqual(len(booked_trucks), 1)
        self.assertEqual(booked_trucks[0][0], truck_id)
        self.assertFalse(booked_trucks[0][6])  # is_available должно быть False

    def test_3_booking_failure_due_to_oversized_cargo(self):
        self.transport_manager.add_truck(**self.test_truck_data)
        trucks = self.transport_manager.get_all_trucks()
        truck_id = trucks[0][0]

        oversized_cargo = {
            'weight': 25.0,
            'length': 12.0,
            'width': 2.0,
            'height': 2.0
        }

        booking_result = self.transport_manager.book_truck(
            truck_id,
            oversized_cargo['weight'],
            oversized_cargo['length'],
            oversized_cargo['width'],
            oversized_cargo['height']
        )

        self.assertFalse(booking_result)

        available_trucks = self.transport_manager.get_available_trucks()
        self.assertEqual(len(available_trucks), 1)
        self.assertTrue(available_trucks[0][6])

    def test_4_truck_lifecycle_management(self):
        # 1. Добавление
        self.transport_manager.add_truck(**self.test_truck_data)
        initial_trucks = self.transport_manager.get_all_trucks()
        truck_id = initial_trucks[0][0]

        # Проверяем начальное состояние
        self.assertEqual(len(initial_trucks), 1)
        self.assertTrue(initial_trucks[0][6])

        # 2. Бронирование
        booking_success = self.transport_manager.book_truck(truck_id, 10.0, 10.0, 2.0, 2.0)
        self.assertTrue(booking_success)

        # Проверяем состояние после бронирования
        booked_trucks = self.transport_manager.get_booked_trucks()
        self.assertEqual(len(booked_trucks), 1)

        # 3. Освобождение
        self.transport_manager.release_truck(truck_id)

        # Проверяем состояние после освобождения
        available_trucks = self.transport_manager.get_available_trucks()
        self.assertEqual(len(available_trucks), 1)
        self.assertTrue(available_trucks[0][6])

        # 4. Удаление
        self.transport_manager.remove_truck(truck_id)

        # Проверяем окончательное состояние
        final_trucks = self.transport_manager.get_all_trucks()
        self.assertEqual(len(final_trucks), 0)

    def test_5_filtering_available_trucks_integration(self):
        trucks_data = [
            ('Volvo Small', 10.0, 8.0, 2.0, 2.0),
            ('Volvo Medium', 20.0, 12.0, 2.4, 2.5),
            ('Volvo Large', 30.0, 15.0, 2.8, 3.0)
        ]

        for truck in trucks_data:
            self.transport_manager.add_truck(*truck)

        # Бронируем один из грузовиков
        all_trucks = self.transport_manager.get_all_trucks()
        self.transport_manager.book_truck(all_trucks[1][0], 15.0, 10.0, 2.0, 2.0)

        # Тестируем фильтрацию без параметров - должны получить 2 доступных
        available_all = self.transport_manager.get_available_trucks()
        self.assertEqual(len(available_all), 2)

        # Тестируем фильтрацию с параметрами - ищем грузовик для груза 25 тонн
        filtered_trucks = self.transport_manager.get_available_trucks(
            capacity=25.0, length=14.0, width=2.5, height=2.8
        )

        # Должен найтись только один подходящий грузовик
        self.assertEqual(len(filtered_trucks), 1)
        self.assertEqual(filtered_trucks[0][1], 'Volvo Large')
        self.assertEqual(filtered_trucks[0][2], 30.0)


class TestGUIIntegration(unittest.TestCase):
    def setUp(self):
        self.root = Tk()
        self.root.withdraw()

    def tearDown(self):
        if self.root:
            self.root.destroy()

    def test_gui_and_manager_integration(self):
        app = TruckManagementApp()

        # Проверяем, что TransportManager был создан
        self.assertIsNotNone(app.transport_manager)
        self.assertIsInstance(app.transport_manager, TransportManager)

        # Проверяем, что виджеты были созданы
        self.assertIsNotNone(app.add_model_entry)
        self.assertIsNotNone(app.all_trucks_listbox)
        self.assertIsNotNone(app.available_trucks_listbox)

        # Проверяем начальное состояние
        initial_trucks = app.transport_manager.get_all_trucks()
        self.assertEqual(len(initial_trucks), 0)


if __name__ == '__main__':
    # Создаем тестовый набор и запускаем тесты
    test_suite = unittest.TestSuite()

    # Добавляем тесты
    test_suite.addTest(TestTransportManagerIntegration('test_1_add_and_retrieve_truck_integration'))
    test_suite.addTest(TestTransportManagerIntegration('test_2_successful_booking_workflow'))
    test_suite.addTest(TestTransportManagerIntegration('test_3_booking_failure_due_to_oversized_cargo'))
    test_suite.addTest(TestTransportManagerIntegration('test_4_truck_lifecycle_management'))
    test_suite.addTest(TestTransportManagerIntegration('test_5_filtering_available_trucks_integration'))
    test_suite.addTest(TestGUIIntegration('test_gui_and_manager_integration'))

    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
