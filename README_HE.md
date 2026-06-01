# מדריך מערכת בעברית - Multi-Agent Translation Pipeline

## מטרת המערכת
המערכת מדגימה תהליך של כמה סוכני AI שעובדים בשרשרת תרגום:
1. תרגום מאנגלית לצרפתית
2. תרגום מצרפתית לעברית
3. תרגום מעברית חזרה לאנגלית
4. השוואה וקטורית בין הטקסט המקורי באנגלית לבין הטקסט הסופי באנגלית

המטרה היא למדוד **Semantic Drift** (סטייה סמנטית) שנוצרת כאשר מעבירים משמעות דרך כמה שפות.

## איך זה אמור לעבוד (זרימת עבודה)
1. קוראים את הטקסט המקורי מתוך `input/01_original.md`.
2. Agent 1 מתרגם EN -> FR ושומר ל-`output/02_french_translation.md`.
3. Agent 2 מתרגם FR -> HE ושומר ל-`output/03_hebrew_translation.md`.
4. Agent 3 מתרגם HE -> EN ושומר ל-`output/04_back_to_english.md`.
5. כלי ההשוואה הופך את שני הטקסטים (מקורי + סופי) ל-embeddings,
   מחשב cosine similarity, ושומר דוח ב-`output/05_vector_comparison_report.md`.

## מבנה הפרויקט
- `app_gui.py` - GUI ויזואלי מלא ב-Streamlit לכל הפייפליין (כולל תמלול אודיו)
- `run_pipeline.py` - מנהל התהליך מקצה לקצה
- `src/pipeline.py` - לוגיקת pipeline משותפת ל-CLI ול-GUI
- `src/config.py` - קונפיגורציה מהסביבה (מודלים, נתיבים)
- `src/io_utils.py` - קריאה/כתיבה של קבצי Markdown
- `src/agents/base_translator.py` - מחלקת בסיס לסוכני תרגום
- `src/agents/en_to_fr_agent.py` - סוכן EN -> FR
- `src/agents/fr_to_he_agent.py` - סוכן FR -> HE
- `src/agents/he_to_en_agent.py` - סוכן HE -> EN
- `src/tools/vector_compare.py` - השוואה וקטורית ודוח
- `skills/` - הגדרות skill/prompt ניתנות לשימוש חוזר
- `start_system.bat` - משגר אוטומטי שמבקש ערכי ENV ומפעיל GUI

## קונפיגורציה - איך לקנפג הכל
המערכת תומכת בשני מצבים:
- `openai` - תרגום אמיתי + embeddings אמיתיים דרך OpenAI API
- `mock` - מצב הדגמה מקומי ללא API (לבדיקות של הזרימה בלבד)

### משתני סביבה נתמכים
- `OPENAI_API_KEY` - חובה למצב `openai`
- `OPENAI_CHAT_MODEL` - ברירת מחדל: `gpt-4o-mini`
- `OPENAI_EMBEDDING_MODEL` - ברירת מחדל: `text-embedding-3-small`
- `PIPELINE_INPUT_PATH` - ברירת מחדל: `input/01_original.md`
- `PIPELINE_OUTPUT_DIR` - ברירת מחדל: `output`

דוגמה ב-PowerShell:
`$env:OPENAI_API_KEY="<your_key_here>"`

## התקנה והרצה מהטרמינל
מתיקיית הפרויקט:

1. יצירת סביבת עבודה:
   - `python -m venv .venv`
   - `.\\.venv\\Scripts\\Activate.ps1`

2. התקנת תלויות:
   - `pip install -r requirements.txt`

3. הרצה במצב OpenAI:
   - `python run_pipeline.py --mode openai`

4. הרצה במצב Mock (בלי מפתח API):
   - `python run_pipeline.py --mode mock`

5. הרצה עם קובץ קלט מותאם:
   - `python run_pipeline.py --input input/01_original.md`

## הרצה ויזואלית (GUI)
1. התקנת תלויות:
   - `pip install -r requirements.txt`
2. הגדרת מפתח OpenAI (לתרגום אמיתי):
   - `$env:OPENAI_API_KEY="<your_key_here>"`
3. הרצת הממשק:
   - `streamlit run app_gui.py`
4. בתוך המסך:
   - בשלב 1 מגדירים Runtime Setup (API Key + Models + Output)
   - בשלב 2 בוחרים Text או Audio לתמלול דרך OpenAI
   - בשלב 3 לוחצים על **Run Full Pipeline (Real API)**
   - צופים בכל שלבי התרגום + מדדי דמיון באופן ויזואלי

## הרצה מהירה עם BAT (מומלץ להצגה למרצה)
1. דאבל-קליק על `start_system.bat`
2. בחלון הראשון ממלאים את כל ערכי ה-ENV:
   - `OPENAI_API_KEY`
   - `OPENAI_CHAT_MODEL`
   - `OPENAI_EMBEDDING_MODEL`
   - `OPENAI_TRANSCRIPTION_MODEL`
   - `PIPELINE_OUTPUT_DIR`
3. ה-BAT יוצר/מעדכן `.env`, מתקין תלויות, ומפעיל אוטומטית את ה-GUI.

## הפלטים שנוצרים בכל הרצה
- `output/02_french_translation.md`
- `output/03_hebrew_translation.md`
- `output/04_back_to_english.md`
- `output/05_vector_comparison_report.md`

## איך לקרוא את דוח ההשוואה הווקטורית
בדוח (`05_vector_comparison_report.md`) תראה:
- השיטה שבה בוצעה ההשוואה
- ציון `cosine similarity` (בדרך כלל בין 0 ל-1, גבוה יותר = דמיון סמנטי גבוה יותר)
- `cosine distance` (נמוך יותר = פחות סטייה סמנטית)
- הסבר קצר בשפה טבעית על רמת השימור של המשמעות

## התאמות עתידיות פשוטות
1. החלפת שפות - יוצרים Agents חדשים ומעדכנים את סדר השלבים ב-`run_pipeline.py`.
2. החלפת מודלים - דרך משתני סביבה בלי לשנות קוד.
3. הרחבת מדדים - אפשר להוסיף BLEU/BERTScore/COMET בנוסף ל-cosine similarity.
4. ניתוח לפי משפטים - כדי לראות בדיוק איפה המשמעות השתנתה לאורך השרשרת.
