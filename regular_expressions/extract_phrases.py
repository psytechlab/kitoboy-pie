import re

patterns = {
    "phone": r"\+?[78][-( ]?\d{3}\)?[- ]?\d{3}[- ]?\d{2}[- ]?\d{2}",
    "bank_card": r"\b(?:\d{4}[- ]?){3}\d{4}\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    "telegram": r"(?:t\.me|telegram\.me)/[a-zA-Z0-9_]+",
    "vk": r"vk\.com/[a-zA-Z0-9_]+"
}

def find_patterns(text): 
    results = {key: re.findall(pattern, text) for key, pattern in patterns.items()}
    
    for key, matches in results.items():
        print(f"\n{key} found:")
        for match in matches:
            print(match)

text = '''
+7(495)123-45-67  
8-905-123-45-67   
89051234567  
+7(812)9999999  
8(812)999-99-99  
+7-911-777-88-99  

1234-5678-9012-3456  
1234 5678 9012 3456  
1234567890123456  

example@yandex.com  
test.email@domain.co.uk  
user123@gmail.ru  
test_email-88@test-domain.io  
mail@sub.domain.com  

t.me/test 
telegram.me/test_user123  
https://t.me/joinchat/

vk.com/id123456  
vk.com/username  
https://vk.com/club987654  
vk.com/user123456  
'''
find_patterns(text)
