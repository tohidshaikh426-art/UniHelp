# Fix public_url reference in view_ticket.html
with open('templates/view_ticket.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace ticket.public_url with just public_url (since it's passed separately to render_template)
content = content.replace('ticket.public_url', 'public_url')

# Write back
with open('templates/view_ticket.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed public_url references in view_ticket.html!")
print("   Changed: ticket.public_url → public_url")
