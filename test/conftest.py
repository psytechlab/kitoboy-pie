
import pytest

@pytest.fixture
def phone_number_collection():
    phone_numbers = """+7(495)123-45-67
8-905-123-45-67
89051234567
+7(812)9999999
8(812)999-99-99
+7-911-777-88-99"""
    phone_numbers = phone_numbers.split("\n")
    input_json = {"inputs":[{"name":"text_input","shape":[len(phone_numbers),1],"datatype":"BYTES","data": phone_numbers}]}
    return (input_json, ["PHONE_NUMBER"] * len(phone_numbers))

@pytest.fixture
def bank_card_collection():
    examples = """1234-5678-9012-3456
1234 5678 9012 3456
1234567890123456"""
    examples = examples.split("\n")
    input_json = {"inputs":[{"name":"text_input","shape":[len(examples),1],"datatype":"BYTES","data": examples}]}
    return (input_json, ["BANK_CARD_NUMBER"] * len(examples))

@pytest.fixture
def emails_collection():
    examples = """example@yandex.com
test.email@domain.co.uk
user123@gmail.ru
test_email-88@test-domain.io
mail@sub.domain.com"""
    examples = examples.split("\n")
    input_json = {"inputs":[{"name":"text_input","shape":[len(examples),1],"datatype":"BYTES","data": examples}]}
    return (input_json, ["EMAIL"] * len(examples))

@pytest.fixture
def telegram_link_collection():
    examples = """t.me/test
telegram.me/test_user123
https://t.me/joinchat/"""
    examples = examples.split("\n")
    input_json = {"inputs":[{"name":"text_input","shape":[len(examples),1],"datatype":"BYTES","data": examples}]}
    return (input_json, ["TELEGRAM"] * len(examples))

@pytest.fixture
def vk_link_collection():
    examples = """vk.com/id123456
vk.com/username
https://vk.com/club987654
vk.com/user123456"""
    examples = examples.split("\n")
    input_json = {"inputs":[{"name":"text_input","shape":[len(examples),1],"datatype":"BYTES","data": examples}]}
    return (input_json, ["VK"] * len(examples))

@pytest.fixture
def ner_collection():
    examples = """я живу в Москве
    меня зовут Иванов Иван
    я работаю в Общеобразовательной Школе 58"""
    examples = examples.split("\n")
    input_json = {"inputs":[{"name":"text_input","shape":[len(examples),1],"datatype":"BYTES","data": examples}]}
    return (input_json, ["LOC", "PER", "ORG"])

@pytest.fixture
def multiple_entity_collection():
    examples = ["Меня зовут Иван Петров, мой номер +7(495)123-45-67"]
    input_json = {"inputs":[{"name":"text_input","shape":[len(examples),1],"datatype":"BYTES","data": examples}]}
    return (input_json, ["PER;PHONE_NUMBER"])