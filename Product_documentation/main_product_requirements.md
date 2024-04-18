

# Introduction
This file contains the main requirements related to the product

Links:
- [Q&A List Message](qa_list_message.md)
- [Promotions and Offers List Message](promotions_list_message.md):



# Textual requirements

```md
Структура боту: 
- Клієнт обирає <start>, щоб запустити бота
-> Привіт, це магазин твоїх улюблених кейсів Orientalcase [:white_heart:] Обери, що цікавить найбільше?
	- Хочу оформити замовлення  
		-> Підкажіть вашу модель телефону/ MacBook/ AirPods?[ відповідь клієнта ]
		-> Який кейс ви обрали?(можете написати назву або надіслати фото/скріншот)
		-> Після того, як надішлете бажаний кейс, тоді натискайте кнопку «Далі», щоб продовжити замовлення
		-> < кнопка далі >
		-> Буде зручно повна оплата чи накладеним платежем з передплатою? ( передплата 150 грн )
			- < кнопка повна оплата >  
			- < кнопка накладний платіж >
		-> Відправка протягом 2-х робочих днів після оплати! [:smiling_face_with_3_hearts:] Надішліть, будь-ласка, квитанцію або скрін про оплату[ тут додати посилання на оплату ]  
		-> Оберіть варіант доставки
			- < кнопка нова пошта >  
				- Вкажіть дані для відправки:
				  Місто та відділення нової пошти
				  ПІБ
				  Номер телефону
			- < кнопка самовивіз > 
				- Чекаємо вас за адресою м. Київ, вул. Саксаганського, 77 з понеділка по п’ятницю з 10 до 19
			- < кнопка міжнародна доставка >
				- ?
			- Дякую, ми отримали ваше замовлення, наш менеджер зв’яжеться з вами якнайшвидше для підтвердження![:heart:]
		
	- Відповідь на популярні запитання 
		- [Q&A List Message]

	- Хочу побачити бестселери  
		- ? [Link to website]

	- Акції та спеціальні пропозиції
		- [Promotions and Offers List Message]
```


# Mermaid flowchart

```mermaid
flowchart TD
    Start["/start"] 
    Greeting["Привіт, це магазин твоїх улюблених кейсів Orientalcase ![:white_heart:] <br> Обери, що цікавить найбільше?"]
    Start --> Greeting
    
    %% Order - Хочу оформити замовлення
    Greeting ----> Order["[button]<br>Хочу оформити замовлення"]

    subgraph ORDER[ORDER]
    Order --> Q_Modeltype["Підкажіть вашу модель телефону/ MacBook/ AirPods?"]
    Q_Modeltype --> |User input| Q_Casetype["Який кейс ви обрали? <br> (можете написати назву або надіслати фото/скріншот) <br> Після того, як надішлете бажаний кейс, тоді натискайте кнопку «Далі», щоб продовжити замовлення"]
    Q_Casetype --> |User input| Next["[button]<br>Далі"]
    Next --create order--> order_id 
    end

    subgraph payment_id
    Next --> Payment["Буде зручно повна оплата чи накладеним платежем з передплатою (передплата 150 грн)? "]
    Payment_approve["Відправка протягом 2-х робочих днів після оплати! <br> Надішліть, будь-ласка, квитанцію або скрін про оплату (тут додати посилання на оплату)"]

    Payment --> Full_payment["[button]<br> Повна оплата"] --> Payment_approve
    Payment --> Cash_on_deliery["[button]<br> Накладний платіж"] --> Payment_approve
    end

    subgraph delivery_id
    Payment_approve --> Delivery_select["Оберіть варіант доставки"]
    Delivery_select --> Nova_post_btn["[button]<br> Нова Пошта"] --> Nova_post["Вкажіть дані для відправки: <br> Місто та відділення нової пошти, <br> ПІБ, <br> Номер телефону"] 
    Delivery_select --> Pickup_btn["[button]<br> Самовивіз"] --> Pickup["Чекаємо вас за адресою м. Київ, вул. Саксаганського, 77 з понеділка по п’ятницю з 10 до 19"]
    Delivery_select --> Int_delivery_btn["[button]<br> Міжнародна доставка"] --> Int_delivery["Вкажіть дані для відправки"]

    Order_success["Дякую, ми отримали ваше замовлення. <br> Наш менеджер зв’яжеться з вами якнайшвидше для підтвердження![:heart:]"]
    Nova_post -->|User input| Order_success
    Pickup --> Order_success
    Int_delivery --> |User input| Order_success
    end

    %% Q&A Block
    Greeting --> QA["Відповідь на популярні запитання"]
    QA --> QA_list["[Q&A List Message]"]

    %% Bestsellers
    Greeting --> Bestsellers["Хочу побачити бестселери"]
    Bestsellers --> Bestsellers_link["{Link to website}"]

    %% Promotions
    Greeting --> Promotions["Акції та спеціальні пропозиції"]
    Promotions --> Promotions_list["{Promotions and Offers List Message}"]
```

