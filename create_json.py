import json
import subprocess

# Выполняем команду dumpdata и получаем данные
result = subprocess.run(
    ['python', 'manage.py', 'dumpdata', '--indent', '2'],
    capture_output=True,
    text=True
)

# Сохраняем данные в файл с ensure_ascii=False
with open('new.json', 'w', encoding='utf-8') as f:
    json.dump(json.loads(result.stdout), f, ensure_ascii=False, indent=4)