import re
import yaml

def has_context(text, match, context_words, window=50):
    """Проверка контекста для сущностей"""
    start = max(0, match.start() - window)
    end = min(len(text), match.end() + window)
    context = text[start:end].lower()
    return any(word.lower() in context for word in context_words if isinstance(word, str) and word)


def check_snils_checksum(snils):
    """Проверка контрольной суммы СНИЛС"""
    digits = re.sub(r'\D', '', snils)
    if len(digits) != 11:
        return False

    # Разделяем на номер и контрольную сумму
    number = digits[:9]
    expected = int(digits[9:])

    # Расчет контрольной суммы
    total = 0
    for i, digit in enumerate(number, 1):
        total += int(digit) * (10 - i)

    if total < 100:
        actual = total
    elif total in (100, 101):
        actual = 0
    else:
        actual = total % 101
        if actual > 100:
            actual = 0

    return actual == expected


def check_inn_individual_checksum(inn):
    """Проверка контрольной суммы для ИНН физического лица (12 цифр)"""
    digits = re.sub(r'\D', '', inn)
    if len(digits) != 12:
        return False

    # Коэффициенты для 11-го разряда (n11)
    coeff_11 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
    # Коэффициенты для 12-го разряда (n12)
    coeff_12 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]

    # Рассчитываем 11-ю цифру
    total_11 = 0
    for i in range(10):
        total_11 += int(digits[i]) * coeff_11[i]
    n11_calc = (total_11 % 11) % 10

    # Рассчитываем 12-ю цифру
    total_12 = 0
    for i in range(11):
        total_12 += int(digits[i]) * coeff_12[i]
    n12_calc = (total_12 % 11) % 10

    # Сравниваем с реальными цифрами
    return n11_calc == int(digits[10]) and n12_calc == int(digits[11])


def check_inn_legal_checksum(inn):
    """Проверка контрольной суммы для ИНН юридического лица (10 цифр)"""
    digits = re.sub(r'\D', '', inn)
    if len(digits) != 10:
        return False

    # Коэффициенты для расчета контрольной суммы
    coeff = [2, 4, 10, 3, 5, 9, 4, 6, 8]

    total = 0
    for i in range(9):
        total += int(digits[i]) * coeff[i]

    n10_calc = (total % 11) % 10

    return n10_calc == int(digits[9])


def check_luhn(card_number):
    """
    Проверка номера банковской карты по алгоритму Луна
    Возвращает True, если номер корректен, иначе False
    """
    # Очищаем от разделителей
    digits = re.sub(r'\D', '', card_number)

    # Проверка длины (обычно 16, но бывает 13-19)
    if len(digits) < 13 or len(digits) > 19:
        return False

    total = 0
    reverse_digits = digits[::-1]

    for i, d in enumerate(reverse_digits):
        num = int(d)
        if i % 2 == 1:  # нечетные позиции (с конца)
            num *= 2
            if num > 9:
                num -= 9
        total += num

    return total % 10 == 0


def check_iban(iban):
    """
    Проверка IBAN по алгоритму MOD 97 (ISO 7064)
    Возвращает True, если IBAN корректен
    """
    import re

    # Очищаем от пробелов и дефисов
    iban = re.sub(r'[\s\-]', '', iban).upper()

    if not (15 <= len(iban) <= 34):
        return False

    # Перемещаем первые 4 символа в конец
    rearranged = iban[4:] + iban[:4]

    # Преобразуем буквы в цифры (A=10, B=11, ..., Z=35)
    converted = ''
    for char in rearranged:
        if char.isdigit():
            converted += char
        else:
            converted += str(ord(char) - ord('A') + 10)

    return int(converted) % 97 == 1


def check_s10_checksum(track):
    """
    Проверка контрольной суммы международного трек-номера S10.
    Возвращает True, если контрольная цифра корректна.
    """
    track = track.upper().strip()
    if len(track) != 13:
        return False

    if not (track[0:2].isalpha() and track[11:13].isalpha()):
        return False

    if not track[2:11].isdigit():
        return False

    # Извлекаем 8 цифр серийного номера
    serial = track[2:10]
    # Извлекаем контрольную цифру (позиция 11)
    check_digit = int(track[10])

    # Веса для 8 цифр
    weights = [8, 6, 4, 2, 3, 5, 9, 7]

    # Расчет контрольной суммы
    total = 0
    for i, digit in enumerate(serial):
        total += int(digit) * weights[i]

    # Расчет по алгоритму MOD 11
    c = 11 - (total % 11)
    if c == 10:
        c = 0
    elif c == 11:
        c = 5

    return c == check_digit


import ipaddress
def check_ip(ip_string):
    """
    Проверяет, является ли строка валидным IP-адресом (IPv4 или IPv6).
    Использует встроенную библиотеку ipaddress.
    """
    try:
        ip_string = ip_string.strip()

        # Пытаемся распарсить как IP
        ip = ipaddress.ip_address(ip_string)

        # Если успешно - возвращаем True
        return True
    except ValueError:
        # Невалидный IP
        return False


def extract_from_yaml(text, yaml_path):
    """
    Извлекает все сущности из YAML-файла
    """
    with open(yaml_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    if not config:
        return []

    context_dependent_entities = [

        'PASSPORT_RF', 'DRIVER_LICENSE', 'STS', 'PASSPORT_INTERNATIONAL',
        'REFUGEE_ID', 'RESIDENCE_PERMIT', 'OMS', 'GENSHIN_UID', 'LARGE_FAMILY_ID',

        'AGE', 'BIRTH_DATE', 'COMBAT_VETERAN_ID','MARRIAGE_CERTIFICATE'

        'EDUCATION_DOC', 'WORK_BOOK', 'MILITARY_ID', 'CRIMINAL_RECORD_CERTIFICATE'
    ]
    entities_with_checksum = {
        'SNILS': check_snils_checksum,
        'INN_INDIVIDUAL': check_inn_individual_checksum,
        'INN_LEGAL': check_inn_legal_checksum,
        'BANK_CARD': check_luhn,
        'IBAN': check_iban,
        'TRACK_INTERNATIONAL': check_s10_checksum,
        'IP_ADDRESS': check_ip
    }

    all_matches = []

    for entity_name, entity_config in config.items():
        if 'patterns' not in entity_config:
            continue

        for pattern in entity_config['patterns']:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                value = match.group()
                context_found = has_context(text, match, entity_config.get('context', []))

                if entity_name in context_dependent_entities and not context_found:
                    continue
                # Проверка контрольных сумм
                if entity_name in entities_with_checksum:
                    check_func = entities_with_checksum[entity_name]
                    is_valid = check_func(value)

                    if not is_valid:
                        continue
                    has_checksum = True
                else:
                    has_checksum = 'N/A'
                all_matches.append({
                    'type': entity_name,
                    'value': value,
                    'start': match.start(),
                    'end': match.end(),
                    'has_context': context_found,
                    'has_checksum': has_checksum
                })


    return all_matches


from pathlib import Path


def extract_all(text, config_dir='configs'):
    """Прогоняет текст через все YAML-файлы в папке"""
    all_matches = []
    config_path = Path(config_dir)

    for yaml_file in config_path.glob('*.yaml'):
        matches = extract_from_yaml(text, str(yaml_file))
        all_matches.extend(matches)

    return all_matches


def resolve_conflicts(matches):
    if not matches:
        return []

    # Сортируем по длине (от самых длинных к коротким)
    # и по наличию контекста/чек-суммы
    # Это гарантирует, что более вероятные сущности мы рассмотрим первыми
    matches.sort(key=lambda x: (
        len(x['value']),
        (x.get('has_checksum') is True or x.get('has_context') is True)
    ), reverse=True)
    final_matches = []

    for current in matches:
        is_overlapping = False
        for accepted in final_matches:
            # Проверяем пересечение координат текущей сущности с уже принятыми
            # Пересечение есть, если max(start) < min(end)
            if max(current['start'], accepted['start']) < min(current['end'], accepted['end']):
                is_overlapping = True
                break

        if not is_overlapping:
            final_matches.append(current)

    # Возвращаем отсортированными по порядку появления в тексте
    return sorted(final_matches, key=lambda x: x['start'])

examples = 'examples.yaml'
with open(examples, 'r', encoding='utf-8') as f:
    example_load = yaml.safe_load(f)
    for example_name, example_text in example_load.items():
        print('=' * 10, example_name, '=' * 10)

        text_to_process = example_text[0]
        print(text_to_process)
        print('-' * 30)

        raw_matches = extract_all(text=text_to_process, config_dir='configs')

        clean_matches = resolve_conflicts(raw_matches)

        for r in clean_matches:
            checksum = r.get('has_checksum', 'N/A')
            print(f"{r['type']}: {r['value']} (context={r['has_context']}, checksum={checksum})")

        print('-' * 30, end='\n')