from typing import List, Dict, Tuple
from dataclasses import dataclass


def validate_rod(length: int, prices: List[int]) -> None:
    if length <= 0:
        raise ValueError("Довжина стрижня повинна бути > 0")
    if not prices:
        raise ValueError("Масив цін не може бути порожнім")
    if len(prices) != length:
        raise ValueError("Довжина масиву цін повинна відповідати довжині стрижня")
    if any(p <= 0 for p in prices):
        raise ValueError("Усі ціни повинні бути > 0")


def is_better(a: Tuple[int, int], b: Tuple[int, int]) -> bool:
    return a[0] > b[0] or (a[0] == b[0] and a[1] < b[1])


def build_result(length: int, profit: int, first: Dict[int, int]) -> Dict:
    cuts = []
    n = length
    while n > 0:
        cuts.append(first[n])
        n -= first[n]
    cuts.sort(reverse=True)
    return {
        "max_profit": profit,
        "cuts": cuts,
        "number_of_cuts": len(cuts) - 1,
        "profit_per_unit": round(profit / length, 2),
    }


def rod_cutting_memo(length: int, prices: List[int]) -> Dict:
    validate_rod(length, prices)
    memo = {0: (0, 0)}
    first = {}

    def solve(n: int) -> Tuple[int, int]:
        if n in memo:
            return memo[n]
        best = (-1, 0)
        for i in range(1, n + 1):
            profit, pieces = solve(n - i)
            candidate = (prices[i - 1] + profit, pieces + 1)
            if is_better(candidate, best):
                best = candidate
                first[n] = i
        memo[n] = best
        return best

    max_profit, _ = solve(length)
    return build_result(length, max_profit, first)


def rod_cutting_table(length: int, prices: List[int]) -> Dict:
    validate_rod(length, prices)
    best = [0] * (length + 1)
    pieces = [0] * (length + 1)
    first = [0] * (length + 1)
    for n in range(1, length + 1):
        best[n] = -1
        for i in range(1, n + 1):
            candidate = (prices[i - 1] + best[n - i], pieces[n - i] + 1)
            if is_better(candidate, (best[n], pieces[n])):
                best[n], pieces[n] = candidate
                first[n] = i
    return build_result(length, best[length], dict(enumerate(first)))


def run_tests():
    test_cases = [
        {"length": 5, "prices": [2, 5, 7, 8, 10], "name": "Базовий випадок"},
        {"length": 3, "prices": [1, 3, 8], "name": "Оптимально не різати"},
        {"length": 4, "prices": [3, 5, 6, 7], "name": "Рівномірні розрізи"},
        {"length": 4, "prices": [2, 4, 6, 8], "name": "Однаковий прибуток для всіх способів"},
        {"length": 8, "prices": [1, 5, 8, 9, 10, 17, 17, 20], "name": "Класичний приклад"},
    ]

    for test in test_cases:
        print(f"\nТест: {test['name']}")
        print(f"Довжина стрижня: {test['length']}")
        print(f"Ціни: {test['prices']}")

        memo_result = rod_cutting_memo(test['length'], test['prices'])
        print("\nРезультат мемоїзації:")
        print(f"Максимальний прибуток: {memo_result['max_profit']}")
        print(f"Прибуток на одиницю довжини: {memo_result['profit_per_unit']}")
        print(f"Розрізи: {memo_result['cuts']}")
        print(f"Кількість розрізів: {memo_result['number_of_cuts']}")

        table_result = rod_cutting_table(test['length'], test['prices'])
        print("\nРезультат табуляції:")
        print(f"Максимальний прибуток: {table_result['max_profit']}")
        print(f"Прибуток на одиницю довжини: {table_result['profit_per_unit']}")
        print(f"Розрізи: {table_result['cuts']}")
        print(f"Кількість розрізів: {table_result['number_of_cuts']}")

        assert memo_result == table_result, "Результати двох методів не збігаються!"
        print("\nПеревірка пройшла успішно!")


@dataclass
class PrintJob:
    id: str
    volume: float
    priority: int
    print_time: int


@dataclass
class PrinterConstraints:
    max_volume: float
    max_items: int


def validate_jobs(jobs: List[PrintJob], limits: PrinterConstraints) -> None:
    if limits.max_volume <= 0 or limits.max_items <= 0:
        raise ValueError("Обмеження принтера повинні бути > 0")
    for job in jobs:
        if job.volume <= 0 or job.print_time <= 0:
            raise ValueError(f"Модель {job.id}: об'єм і час друку повинні бути > 0")
        if job.priority not in (1, 2, 3):
            raise ValueError(f"Модель {job.id}: пріоритет повинен бути 1, 2 або 3")
        if job.volume > limits.max_volume:
            raise ValueError(f"Модель {job.id} не вміщується в принтер навіть сама")


def optimize_printing(print_jobs: List[Dict], constraints: Dict) -> Dict:
    jobs = [PrintJob(**job) for job in print_jobs]
    limits = PrinterConstraints(**constraints)
    validate_jobs(jobs, limits)

    jobs.sort(key=lambda job: (job.priority, -job.print_time))

    groups = []
    current = []
    current_volume = 0
    for job in jobs:
        if current and (current_volume + job.volume > limits.max_volume
                        or len(current) == limits.max_items):
            groups.append(current)
            current = []
            current_volume = 0
        current.append(job)
        current_volume += job.volume
    if current:
        groups.append(current)

    total_time = sum(max(job.print_time for job in group) for group in groups)

    return {
        "print_order": [job.id for job in jobs],
        "total_time": total_time,
        "groups": [[job.id for job in group] for group in groups],
    }


def test_printing_optimization():
    test1_jobs = [
        {"id": "M1", "volume": 100, "priority": 1, "print_time": 120},
        {"id": "M2", "volume": 150, "priority": 1, "print_time": 90},
        {"id": "M3", "volume": 120, "priority": 1, "print_time": 150}
    ]

    test2_jobs = [
        {"id": "M1", "volume": 100, "priority": 2, "print_time": 120},
        {"id": "M2", "volume": 150, "priority": 1, "print_time": 90},
        {"id": "M3", "volume": 120, "priority": 3, "print_time": 150}
    ]

    test3_jobs = [
        {"id": "M1", "volume": 250, "priority": 1, "print_time": 180},
        {"id": "M2", "volume": 200, "priority": 1, "print_time": 150},
        {"id": "M3", "volume": 180, "priority": 2, "print_time": 120}
    ]

    test4_jobs = [
        {"id": "M1", "volume": 90, "priority": 2, "print_time": 60},
        {"id": "M2", "volume": 110, "priority": 2, "print_time": 200},
        {"id": "M3", "volume": 80, "priority": 1, "print_time": 100},
        {"id": "M4", "volume": 70, "priority": 2, "print_time": 140},
        {"id": "M5", "volume": 60, "priority": 1, "print_time": 160}
    ]

    constraints = {
        "max_volume": 300,
        "max_items": 2
    }

    tests = [
        ("Тест 1 (однаковий пріоритет)", test1_jobs),
        ("Тест 2 (різні пріоритети)", test2_jobs),
        ("Тест 3 (перевищення обмежень)", test3_jobs),
        ("Тест 4 (однаковий пріоритет, різний час друку)", test4_jobs),
    ]
    for i, (name, jobs) in enumerate(tests):
        result = optimize_printing(jobs, constraints)
        print(("\n" if i else "") + name + ":")
        print(f"Порядок друку: {result['print_order']}")
        print(f"Групи друку: {result['groups']}")
        print(f"Загальний час: {result['total_time']} хвилин")


if __name__ == "__main__":
    print("=" * 60)
    print("ЗАВДАННЯ 1. Оптимальне розрізання стрижня (динамічне програмування)")
    print("=" * 60)
    run_tests()

    print("\n\n" + "=" * 60)
    print("ЗАВДАННЯ 2. Оптимізація черги 3D-принтера (жадібний алгоритм)")
    print("=" * 60 + "\n")
    test_printing_optimization()