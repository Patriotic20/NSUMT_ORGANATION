# NSUMT_ORGANIZATION

Ushbu repository NSUMT (Milliy Davlat Boshqaruv va Texnologiya Universiteti) uchun mo‘ljallangan mikroxizmatlarga asoslangan ilovani o‘z ichiga oladi. Tizim bir nechta xizmatlardan iborat bo‘lib, har biri alohida funksiyalarni bajaradi va modul va kengaytiriladigan arxitektura ta’minlaydi.  

## 🛠️ Arxitektura ko‘rinishi

Ilova quyidagi xizmatlardan iborat:

1. **university_auth**  
   - **Maqsad:** Foydalanuvchilarni autentifikatsiya va avtorizatsiya qilish.  
   - **Texnologiyalar:** Python, FastAPI, FastStream, PostgreSQL, RabbitMQ.  
   - **Vazifalar:** Foydalanuvchi login, token yaratish va tekshirish.

2. **university_organization**  
   - **Maqsad:** Universitetdagi tashkilot ma’lumotlarini boshqarish.  
   - **Texnologiyalar:** Python, FastAPI, PostgreSQL.  
   - **Vazifalar:** Fakultetlar, bo‘limlar va boshqa tashkilot birliklari bilan bog‘liq CRUD operatsiyalarini bajarish.

3. **university_student_test**  
   - **Maqsad:** Talabalarni testdan o‘tkazish va baholash.  
   - **Texnologiyalar:** Python, FastAPI, PostgreSQL.  
   - **Vazifalar:** Test yaratish, baholash va natijalarni kuzatish.

## 🧱 Asosiy texnologiyalar

- **FastAPI:** Zamonaviy va yuqori tezlikdagi Python veb-ramkasi.  
- **FastStream:** Asinxron mikroxizmatlar qurish uchun event-driven ramka.  
- **PostgreSQL:** Kuchli, ochiq manbali ma’lumotlar bazasi.  
- **RabbitMQ:** Xizmatlar o‘rtasida xabarlarni yuborish va olish uchun broker.  
- **Docker & Docker Compose:** Ko‘p konteynerli ilovalarni boshqarish va konteynerlashtirish vositalari.  

## 🚀 Ishga tushirish

### Talablar

- Python 3.12+  
- Docker & Docker Compose  
- PostgreSQL  
- RabbitMQ  

### O‘rnatish

1. **Repositoryni klonlash:**

```bash
git clone https://github.com/Patriotic20/NSUMT_ORGANATION.git
cd NSUMT_ORGANATION
```
## 📂 Loyihaning tuzilishi

NSUMT_ORGANATION/
│
├── university_auth/
│ ├── app/
│ ├── requirements.txt
│ └── ...
│
├── university_organization/
│ ├── app/
│ ├── requirements.txt
│ └── ...
│
├── university_student_test/
│ ├── app/
│ ├── requirements.txt
│ └── ...
│
├── docker-compose.yml
└── nginx.conf
