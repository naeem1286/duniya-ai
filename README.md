Duniya AI — ویب سائٹ پروجیکٹ

یہ ایک responsive ویب سائٹ کا ابتدائی ورژن ہے، جو موبائل اور کمپیوٹر کے browser میں چلتا ہے۔

اہم بات:
- یہ خود سے نیا AI model نہیں ہے۔ یہ ایک AI provider کے model سے محفوظ server-side connection بناتا ہے۔
- جب تک hosting میں AI_API_KEY اور درست model/provider settings نہیں لگیں گی، حقیقی AI جواب نہیں دے گا۔
- API key کبھی index.html یا browser JavaScript میں نہ ڈالیں۔
- اس پروجیکٹ میں basic safety instructions ہیں، مگر کوئی بھی AI مکمل طور پر غلطی سے پاک یا ہر misuse کو روکنے کی ضمانت نہیں دے سکتا۔
- Free اور Pro کے قیمت والے کارڈ صرف ابھی دکھائے جانے والے منصوبے ہیں؛ subscription، login، billing، usage limits اور payments ابھی فعال نہیں ہیں۔

آن لائن چلانے کا آسان راستہ:
1. ZIP فائل extract کریں۔
2. اس فولڈر کو کسی cloud hosting service پر upload/connect کریں جو Python web apps چلاتی ہو (مثلاً Render)۔
3. hosting کی Environment Variables میں AI_API_KEY شامل کریں۔
4. AI_MODEL کو اپنے provider کے supported model کے مطابق رکھیں۔
5. Deploy کریں اور بننے والا public website URL موبائل اور کمپیوٹر پر کھولیں۔

اگر API provider مختلف base URL استعمال کرتا ہے تو AI_BASE_URL بھی set کریں۔
AI service کی قیمت اور free quota provider کے حساب سے مختلف ہوگی؛ unlimited free usage فرض نہ کریں۔

فائلیں:
- app.py: server اور AI connection
- templates/index.html: ویب سائٹ کا صفحہ
- static/style.css: responsive design
- static/app.js: chat UI
- render.yaml / Procfile: hosting configuration
