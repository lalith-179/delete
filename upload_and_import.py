import os
import subprocess
import zipfile
import shutil

print("Step 1: Extracting fixtures.zip...")
# Extract the fixtures.zip file
with zipfile.ZipFile('fixtures.zip', 'r') as zip_ref:
    # Create fixtures directory if it doesn't exist
    os.makedirs('fixtures', exist_ok=True)
    zip_ref.extractall('fixtures')

print("Step 2: Running import_data.py to import fixtures...")
# Run the import_data.py script
result = subprocess.run(['python', 'import_data.py'], capture_output=True, text=True)

if result.returncode == 0:
    print(result.stdout)
    print("Data import completed successfully!")
else:
    print(f"Error during import: {result.stderr}")
    print(result.stdout)

print("\nYour movies, shows, banners, and other data have been imported to the database.")
print("You can now access them through the admin interface or your website.")
