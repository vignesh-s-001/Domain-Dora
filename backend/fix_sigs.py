content = open('app/services/technology/signatures.py', 'r', encoding='utf-8').read()
# Remove all inline (?i) flags since re.IGNORECASE is already passed in check_rules
fixed = content.replace('(?i)', '')
open('app/services/technology/signatures.py', 'w', encoding='utf-8').write(fixed)
print('Done. Removed all inline (?i) flags.')
