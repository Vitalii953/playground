# Run deeply nested Python files as modules instantly
run() {
    # Step 1: Find the first matching file fast using 'fd' (Rust)
    # Note: If on Ubuntu/Debian, change 'fd' to 'fdfind' if you didn't alias it.
    local filepath=$(fd --type f --max-results 1 "^$1$")

    # If fd isn't installed, you can fallback to the C-based 'find':
    # local filepath=$(find . -name "$1" -type f -print -quit)

    if [[ -z "$filepath" ]]; then
        echo "Error: Could not find '$1' in the current directory tree."
        return 1
    fi

    # Step 2: Format the path for 'python -m'
    # Strip leading './' (if using find fallback)
    filepath="${filepath#./}"
    # Strip the '.py' extension
    filepath="${filepath%.py}"
    # Convert slashes to dots
    local modpath="${filepath//\//.}"

    # Step 3: Run it
    echo -e "\033[90m> Found at $filepath.py\033[0m"
    echo -e "\033[92m> Executing: python -m $modpath\033[0m"
    python -m "$modpath"
}
