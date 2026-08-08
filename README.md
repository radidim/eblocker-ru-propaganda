# eBlocker RUSSIAN-PROPAGANDA-MAX — автоматично обновяващ се списък

Този пакет превръща статичния ти списък с домейни в **самообновяващ се** eBlocker
списък, хостван на GitHub. eBlocker сочи към един URL и сам го тегли всеки ден.

## Как работи

```
domains-base.txt  ──┐
                     ├──►  update_blocklist.py  ──►  eBlocker_Russian_Propaganda_MAX.txt
sources.txt       ──┘            (обединява, чисти,        (готовият файл, който
(незадължителни                   премахва дубликати,        eBlocker тегли)
 външни източници)                 сортира)
```

- **domains-base.txt** — твоят текущ, ръчно поддържан списък (633 домейна от
  качения файл, изчистен и сортиран).
- **sources.txt** — по избор, за external списъци. Оставен е празен, защото
  публично поддържани, надеждни списъци специално за руска
  държавна пропаганда/дезинформация са рядкост и трябва да се проверяват
  ръчно, преди да се доверя автоматично на съдържанието им (виж коментарите
  вътре във файла как да добавиш такъв, ако намериш подходящ).
- **update_blocklist.py** — обединява двата източника, маха невалидни редове,
  дубликати и генерира финалния файл с хедър (дата, брой домейни).
- **.github/workflows/update.yml** — GitHub Action, който пуска скрипта:
  - всеки ден в 04:00 UTC,
  - при всяко push към `domains-base.txt` / `sources.txt`,
  - или ръчно от таб „Actions“.
  При промяна commit-ва новия `eBlocker_Russian_Propaganda_MAX.txt` обратно
  в репото — тоест "auto-updating" в буквалния смисъл.

## Стъпки за качване в GitHub

1. Създай нов **публичен** repo в GitHub (напр. `eblocker-ru-propaganda`).
   Публичен е необходим, за да работи безплатен "raw" достъп до файла.
2. Качи всички файлове от тази папка в него (през уеб интерфейса с
   "Add file → Upload files", или през `git`):
   ```bash
   cd eblocker-ru-propaganda
   git init
   git add .
   git commit -m "Initial import"
   git branch -M main
   git remote add origin https://github.com/<твоя-акаунт>/eblocker-ru-propaganda.git
   git push -u origin main
   ```
3. Отвори таб **Actions** в repo-то и разреши workflows, ако GitHub попита
   (за нови repo-та Actions обикновено са включени по подразбиране).
4. Изчакай първия автоматичен run (или го пусни ръчно: Actions →
   „Update eBlocker blocklist“ → „Run workflow“), за да се появи файлът
   `eBlocker_Russian_Propaganda_MAX.txt` в главния клон.

## URL за eBlocker

След първия успешен run, суровият файл ще е достъпен на:

```
https://raw.githubusercontent.com/<твоя-акаунт>/eblocker-ru-propaganda/main/eBlocker_Russian_Propaganda_MAX.txt
```

В eBlocker:

1. Отиди на **Blocker → Domain Blocker** (напр. категория „Malware & Phishing“
   или създай собствена категория, ако версията ти позволява).
2. Натисни **ADD**.
3. Име: `Russian Propaganda MAX`.
4. Формат: **Domain list** (обикновен списък с домейни — точно това генерира
   скриптът; `#` в началото на реда се третира като коментар от eBlocker).
5. URL: постави линка отгоре.
6. Активирай **„daily update“** — тогава eBlocker сам ще дърпа обновената
   версия всеки ден, синхронно с GitHub Action-а.
7. **SAVE** → eBlocker тегли и импортира списъка.

## Как да поддържаш списъка занапред

- Ръчно добавяне на домейн: редактирай `domains-base.txt` директно в GitHub
  (или локално + push) → Action-ът автоматично прегенерира крайния файл.
- Добавяне на външен източник: виж инструкциите в `sources.txt`.
- Всичко е plain text — няма нужда от build стъпки на твоя страна.

## Забележка

Скриптът е инженерно "автоматизиращ" (merge + dedupe + хостван URL с daily
pull), но подборът на *кои* домейни влизат в `domains-base.txt` си остава
редакторско решение — препоръчвам периодична ръчна проверка, преди да разчиташ
изцяло на него в production мрежа.
