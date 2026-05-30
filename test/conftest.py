import pytest


def make_input(examples):
    return {
        "inputs": [
            {
                "name": "text_input",
                "shape": [len(examples), 1],
                "datatype": "BYTES",
                "data": examples,
            }
        ]
    }


@pytest.fixture
def phone_number_collection():
    examples = """+7(495)123-45-67
8-905-123-45-67
89051234567
+7(812)9999999
8(812)999-99-99
+7-911-777-88-99""".split("\n")
    return make_input(examples), examples, ["PHONE_NUMBER"] * len(examples)


@pytest.fixture
def bank_card_collection():
    examples = """1234-5678-9012-3456
1234 5678 9012 3456
1234567890123456""".split("\n")
    return make_input(examples), examples, ["BANK_CARD"] * len(examples)


@pytest.fixture
def emails_collection():
    examples = """example@yandex.com
test.email@domain.co.uk
user123@gmail.ru
test_email-88@test-domain.io
mail@sub.domain.com""".split("\n")
    return make_input(examples), examples, ["EMAIL"] * len(examples)


@pytest.fixture
def telegram_link_collection():
    examples = """t.me/test
telegram.me/test_user123
https://t.me/joinchat/""".split("\n")
    return make_input(examples), examples, ["TELEGRAM"] * len(examples)


@pytest.fixture
def vk_link_collection():
    examples = """vk.com/id123456
vk.com/username
https://vk.com/club987654
vk.com/user123456""".split("\n")
    return make_input(examples), examples, ["VK"] * len(examples)


@pytest.fixture
def ner_collection():
    examples = """я живу в Москве
меня зовут Иванов Иван
я работаю в Общеобразовательной Школе 58""".split("\n")
    return make_input(examples), examples, ["ADDRESS", "NAME", "ORGANIZATION"]


@pytest.fixture
def multiple_entity_collection():
    examples = ["Меня зовут Иван Петров, мой номер +7(495)123-45-67"]
    return make_input(examples), examples, [["NAME", "PHONE_NUMBER"]]
