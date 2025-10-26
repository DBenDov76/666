🔧 Deploy to Render.com — Simple Steps (Hebrew)

מה יש בתיקייה:
- app.py — קובץ Flask מעודכן ל-Render (host=0.0.0.0 + PORT מהסביבה)
- templates/index.html — הדף שלך אחד לאחד
- requirements.txt — ספריות נדרשות (Flask, pandas, openpyxl)
- Procfile — אופציונלי (web: python app.py)
- uploads/ — תיקיית העלאות (נוצרת אוטומטית בריצה)
- run_app.bat — להרצה מקומית בלבד (לא נדרש ל-Render)

שלבים:
1) פתח GitHub → New Repository (למשל: winner-generator)
2) העלה את כל הקבצים מתוך התיקייה הזו (Flask_6nums_Render_20251026_1237) — כולל התיקייה templates
3) ברנדר:
   - New → Web Service
   - חבר את GitHub ובחר את הריפו
   - Build Command:  pip install -r requirements.txt
   - Start Command:  python app.py
   - Plan: Free
4) Deploy. בסיום יופיע קישור ציבורי.
5) אם תקבל הודעה על Port — אתה כבר מכוסה (app.py מוגדר נכון).
6) קבצי העלאה (CSV/Excel) נשמרים זמנית בלבד (דיסק זמני). זה תקין — כל העלאה מעובדת מיידית.

טיפים:
- שם התיקייה templates חייב להיות בדיוק templates.
- אם תעדכן קבצים ב-GitHub — Render יעשה Deploy מחדש אוטומטית.
- אם העומס גבוה, יכול להיות דיליי של כמה שניות בעלייה הראשונה (Free plan).
