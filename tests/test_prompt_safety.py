from backend.prompts.extraction_prompt import SYSTEM_EXTRACTION_PROMPT

checks = [
    "Do not perform underwriting decisions.",
    "Do not calculate risk scores.",
    "Do not approve or reject the customer.",
    "Do not make insurance eligibility decisions.",
]

passed = True

for check in checks:
    if check in SYSTEM_EXTRACTION_PROMPT:
        print(f"{check}: PASS")
    else:
        print(f"{check}: FAIL")
        passed = False

print("PASS:", passed)
