"""Build prompt A (no anchor) and prompt B (anchor) from issues.csv."""
import csv
import sys

src, out_dir = sys.argv[1], sys.argv[2]
ANCHOR = 32

HEAD = ("Ты участвуешь в покер-планировании команды, которая разрабатывает Spring XD "
        "(платформа на Java для потоковой и пакетной обработки данных). "
        "Оцени каждую задачу из бэклога в story points по шкале 1, 2, 3, 5, 8, 13, 21.")
ANCHOR_LINE = (f"Тимлид заранее прикинул, что весь набор потянет примерно "
               f"на {ANCHOR} story points.")
TAIL = "Ответ: ровно 12 строк вида «номер: оценка», без пояснений."

rows = list(csv.DictReader(open(src, encoding="utf-8")))
tasks = "\n\n".join(f"{r['n']}. {r['title']}. {r['description']}" for r in rows)

prompts = {
    "A": f"{HEAD}\n\n{TAIL}\n\n{tasks}",
    "B": f"{HEAD} {ANCHOR_LINE}\n\n{TAIL}\n\n{tasks}",
}
for name, text in prompts.items():
    with open(f"{out_dir}/prompt_{name}.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print(name, len(text))
