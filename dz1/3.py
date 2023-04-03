words = ["attribute", "класс", "функция", "type"]
for word in words:
    try:
        print(bytes(word, 'ascii'))
    except Exception:
        print(f"Слово {word} нельзя записать в байтовом формате")
