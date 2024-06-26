# Інструкція з використання боту

## Вступ

- Бот запускається через команду `/start`, таким самим чином і перезапускається діалог

- На етапі замовлення товар може бути автоматично знайдений. 
	- Якщо це відбувається, ціна формується автоматично
	- Якщо товар не знадено, замовлення оформлюється тільки шляхом ручного вводу користувачем 

## Сервер

Наразі бот лежить на сервері Pythonanywhere, де лежать всі файли, які потрібні для функціонування бота:
- база даних
- сам код бота
- файли, потрібні для зміни повідомлень бота

### Перезапущення боту 

Щоб перезапустити бота (Наприклад, для оновлення діалогу чи коду), його потрібно зупинити і запустити ще раз.
Для цього треба:
- Якщо бот запущений
	- зайти в files -> main 
	- в консолі натиснути `ctrl+c`
	- написати `exit()` -> Enter
	- натиснути кнопку `Run`
- Якщо бот не запущений:
	- зайти в files -> main 
	- натиснути кнопку `Run`

### Оновлення файлів

- Файли лежать у files
- Наявні файли можна оновити просто на pythonanywhere, після цього бота треба перезавантажити
- Оновлення файлів можна підключити до github, але це потребує окремо підключення і знання певних команд для консолі

## Зміна деяких повідомлень

Наразі діалог прописаний всередині коду, але деякі повідомлення можна змінити через `data.json` файл (у папці `data`):
- Бестселери 
- Адреса самовивізу
	- в полях Greeting, Address, Time поля address можна редагувати вітання, адресу і час роботи для опції Самовивізу
- Акції - полі shares
- Q&A - в полі pop

- Популярні питання і акції можна додавати нові

## Way for pay

Way for pay потребує попереднього налаштування.
У `.env` файлі лежать наступні дані, які в подальшому мають бути додані користувачем:
- SECRETKEY_WFP = `"flk3409refn54t54t*FNJRET"  `
- merchantAccount = `"test_merch_n1"  `
- merchantDomainName = `"[https://wayforpay.com/freelance.php](https://wayforpay.com/freelance.php)`

Детальніше про те, як знайти ці дані:
- [Створення рахунків (Create invoice) - Документация - Wayforpay](https://wiki.wayforpay.com/view/608996852)

## Повідомлення про замовлення менеджеру

- Повідомлення про замовлення відправляється тільки у кінці діалогу, коли користувач ввів номер телефону

- Дані повідомлення відправляються тільки непусті і залежать також від того, чи був знайдений автоматично кейс через сайт

- Можлива відправка повідомлення у чат менеджеру і у групу, куди доданий менеджер
	- Про те, як налаштувати відправлення:
		- [менеджеру](#MANAGER_ID) 
		- [у групу](#GROUP_ID) 

- Всі зміни для відправки повідомлення відбуваються у  `.env` файлі:


### MANAGER_ID

Для зміни менеджера, якому відправляється повідомлення треба телеграм id користувача

Щоб отримати телеграм id користувача використовується  наступний бот - `@userinfobot` 

Далі в `.env` файлі змінюється  `MANAGER_ID`. 
- Будьте уважні, що `" "` мають залишатися"

### GROUP_ID

Для зміни групи, якій відправляється повідомлення треба:
- додати бота до користувачів групи
- телеграм id групи

#### Додавання бота до групи

- [  How to Add a Bot in Telegram](https://www.alphr.com/add-bot-telegram)

#### Отримання telegram group id

Увійдіть у свій обліковий запис у веб-сайті Telegram і виберіть групу Telegram. 
Тоді в URL-адресі веб-переглядача ви повинні побачити щось схоже на `https://web.telegram.org/k/#-XXXXXXXXX` 
Тоді ідентифікатор, який потрібно використовувати для групи Telegram, це -XXXXXXXXX , де кожен символ X представляє число.

Приклад id - `GROUP_ID = "-982102530"`

Далі в `.env` файлі змінюється  `GROUP_ID`. 
- Будьте уважні, що `" "` мають залишатися"