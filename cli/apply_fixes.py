def apply_fixes(original_code, refactored_code):
    print("\n💬 Do you want to apply the suggested fixes?")
    print("Type 'yes' to apply and save, or 'no' to discard.")

    user_input = input("🔧 Apply fixes? (yes/no): ").strip().lower()

    if user_input == "yes":
        filename = input("💾 Enter filename to save (e.g., fixed_code.py): ").strip()
        try:
            with open(filename, "w") as f:
                f.write(refactored_code)
            print(f"\n✅ Refactored code saved to: {filename}")
        except Exception as e:
            print(f"❌ Error saving file: {e}")
    else:
        print("\n🚫 Fixes were not applied. Original code remains unchanged.")
