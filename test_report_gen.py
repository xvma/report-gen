import pytest
from report_gen import generate_performance_report, group_by

class TestGroupBy:
    """Тесты для функции group_by"""

    def test_group_by_empty_list(self):
        """Тест группировки пустого списка"""
        result = group_by([], key_func=lambda x: x, value_func=lambda x: x)
        assert result == {}

    def test_group_by_simple_values(self):
        """Тест группировки простых значений"""
        data = [1, 2, 3, 4, 5, 6]
        result = group_by(
            data,
            key_func=lambda x: 'even' if x % 2 == 0 else 'odd',
            value_func=lambda x: x
        )
        assert result == {'even': [2, 4, 6], 'odd': [1, 3, 5]}

    def test_group_by_dicts(self):
        """Тест группировки словарей"""
        data = [
            {'category': 'A', 'value': 10},
            {'category': 'B', 'value': 20},
            {'category': 'A', 'value': 30},
            {'category': 'C', 'value': 40},
            {'category': 'B', 'value': 50}
        ]

        result = group_by(
            data,
            key_func=lambda x: x['category'],
            value_func=lambda x: x['value']
        )

        assert result == {
            'A': [10, 30],
            'B': [20, 50],
            'C': [40]
        }

    def test_group_by_with_transformation(self):
        """Тест группировки с преобразованием значений"""
        data = ['apple', 'banana', 'apricot', 'cherry', 'blueberry']

        result = group_by(
            data,
            key_func=lambda x: x[0],  # первая буква
            value_func=lambda x: len(x)  # длина слова
        )

        assert result == {
            'a': [5, 7],
            'b': [6, 9],
            'c': [6]
        }


class TestGeneratePerformanceReport:
    """Тесты для функции generate_performance_report"""

    def test_empty_data(self):
        """Тест с пустыми данными"""
        result = generate_performance_report([])
        assert result == []

    def test_single_position(self):
        """Тест с одной должностью"""
        data = [
            {'position': 'Developer', 'performance': '8.5'},
            {'position': 'Developer', 'performance': '9.0'},
            {'position': 'Developer', 'performance': '7.5'}
        ]

        result = generate_performance_report(data)

        expected = [{'position': 'Developer', 'performance': 8.33}]
        assert len(result) == 1
        assert result[0]['position'] == 'Developer'
        assert abs(result[0]['performance'] - 8.33) < 0.01

    def test_multiple_positions(self):
        """Тест с несколькими должностями"""
        data = [
            {'position': 'Developer', 'performance': '8.0'},
            {'position': 'Developer', 'performance': '9.0'},
            {'position': 'Manager', 'performance': '7.0'},
            {'position': 'Manager', 'performance': '8.0'},
            {'position': 'Analyst', 'performance': '9.5'},
            {'position': 'Developer', 'performance': '7.0'}
        ]

        result = generate_performance_report(data)

        # Проверяем количество уникальных позиций
        assert len(result) == 3

        # Проверяем, что результаты отсортированы по убыванию performance
        performances = [item['performance'] for item in result]
        assert performances == sorted(performances, reverse=True)

        # Проверяем правильность вычисления средних значений
        position_map = {item['position']: item['performance'] for item in result}

        # Developer: (8.0 + 9.0 + 7.0) / 3 = 8.0
        assert abs(position_map['Developer'] - 8.0) < 0.01

        # Manager: (7.0 + 8.0) / 2 = 7.5
        assert abs(position_map['Manager'] - 7.5) < 0.01

        # Analyst: 9.5 / 1 = 9.5
        assert abs(position_map['Analyst'] - 9.5) < 0.01

    def test_performance_as_float_strings(self):
        """Тест с производительностью в виде строк с плавающей точкой"""
        data = [
            {'position': 'QA', 'performance': '6.75'},
            {'position': 'QA', 'performance': '8.25'},
            {'position': 'DevOps', 'performance': '9.99'}
        ]

        result = generate_performance_report(data)

        # Проверяем корректность преобразования строк в float
        assert len(result) == 2

        position_map = {item['position']: item['performance'] for item in result}

        # QA: (6.75 + 8.25) / 2 = 7.5
        assert abs(position_map['QA'] - 7.5) < 0.01

        # DevOps: 9.99 / 1 = 9.99
        assert abs(position_map['DevOps'] - 9.99) < 0.01

    def test_same_performance_different_positions(self):
        """Тест с одинаковой производительностью для разных должностей"""
        data = [
            {'position': 'Frontend', 'performance': '8.0'},
            {'position': 'Backend', 'performance': '8.0'},
            {'position': 'Mobile', 'performance': '8.0'}
        ]

        result = generate_performance_report(data)

        # Все должны иметь одинаковую производительность
        assert len(result) == 3
        for item in result:
            assert abs(item['performance'] - 8.0) < 0.01


# Дополнительные интеграционные тесты
class TestIntegration:
    """Интеграционные тесты"""

    def test_group_by_used_in_performance_report(self):
        """Тест, что group_by корректно используется в generate_performance_report"""
        data = [
            {'position': 'Engineer', 'performance': '10.0'},
            {'position': 'Engineer', 'performance': '8.0'},
            {'position': 'Designer', 'performance': '9.0'}
        ]

        # Проверяем, что group_by работает корректно
        grouped = group_by(
            data,
            key_func=lambda item: item['position'],
            value_func=lambda item: float(item['performance'])
        )

        assert grouped == {
            'Engineer': [10.0, 8.0],
            'Designer': [9.0]
        }

        # Проверяем, что generate_performance_report дает ожидаемый результат
        result = generate_performance_report(data)
        assert len(result) == 2

        position_map = {item['position']: item['performance'] for item in result}
        assert abs(position_map['Engineer'] - 9.0) < 0.01  # (10.0 + 8.0) / 2
        assert abs(position_map['Designer'] - 9.0) < 0.01  # 9.0 / 1