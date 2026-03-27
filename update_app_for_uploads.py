# Update app.py to add file upload blueprint import and registration
import re

# Read app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add import after flask_mail import
if 'from file_uploads import file_uploads' not in content:
    content = content.replace(
        'from flask_mail import Mail, Message\n\n# AI Chatbot Integration',
        'from flask_mail import Mail, Message\n\n# NEW: Import file upload blueprint\nfrom file_uploads import file_uploads\n\n# AI Chatbot Integration'
    )
    print("✅ Added import statement")

# Register blueprint before app.run
if 'app.register_blueprint(file_uploads)' not in content:
    content = content.replace(
        "if __name__ == '__main__':",
        "# Register file upload blueprint\napp.register_blueprint(file_uploads)\n\nif __name__ == '__main__':"
    )
    print("✅ Registered blueprint")

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ app.py updated successfully!")
