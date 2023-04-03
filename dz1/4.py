words = ["разработка", "администрирование", "protocol", "standard"]
words_bytes = []
for word in words:
    words_bytes.append(word.encode('utf8'))
print(words_bytes)

words2 = []
for word in words_bytes:
    words2.append(word.decode('utf8'))

print(words2)
