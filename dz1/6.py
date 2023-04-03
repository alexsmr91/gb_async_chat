words = ["сетевое программирование", "сокет", "декоратор"]
with open("test_file.txt", "w") as f:
    for word in words:
        f.write(word+"\n")

with open("test_file.txt", "r", encoding="utf8") as f:
    try:
        print(f.readlines())
    except Exception:
        print("Не удалось")
