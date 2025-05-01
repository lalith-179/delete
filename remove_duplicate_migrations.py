import os
import shutil

# List of files to remove
files_to_remove = [
    # contenttypes migrations
    '.venv/Lib/site-packages/django/contrib/contenttypes/migrations/0001_initial_1.py',
    '.venv/Lib/site-packages/django/contrib/contenttypes/migrations/0002_remove_content_type_name_1.py',
    
    # sessions migrations
    '.venv/Lib/site-packages/django/contrib/sessions/migrations/0001_initial_1.py',
    
    # admin migrations
    '.venv/Lib/site-packages/django/contrib/admin/migrations/0001_initial_1.py',
    '.venv/Lib/site-packages/django/contrib/admin/migrations/0002_logentry_remove_auto_add_1.py',
    '.venv/Lib/site-packages/django/contrib/admin/migrations/0003_logentry_add_action_flag_choices_1.py',
    
    # auth migrations
    '.venv/Lib/site-packages/django/contrib/auth/migrations/0001_initial_1.py',
    '.venv/Lib/site-packages/django/contrib/auth/migrations/0002_alter_permission_name_max_length_1.py',
    '.venv/Lib/site-packages/django/contrib/auth/migrations/0003_alter_user_email_max_length_1.py',
    '.venv/Lib/site-packages/django/contrib/auth/migrations/0004_alter_user_username_opts_1.py',
    '.venv/Lib/site-packages/django/contrib/auth/migrations/0005_alter_user_last_login_null_1.py',
    '.venv/Lib/site-packages/django/contrib/auth/migrations/0006_require_contenttypes_0002_1.py',
    '.venv/Lib/site-packages/django/contrib/auth/migrations/0007_alter_validators_add_error_messages_1.py',
    '.venv/Lib/site-packages/django/contrib/auth/migrations/0008_alter_user_username_max_length_1.py',
    '.venv/Lib/site-packages/django/contrib/auth/migrations/0009_alter_user_last_name_max_length_1.py',
    '.venv/Lib/site-packages/django/contrib/auth/migrations/0010_alter_group_name_max_length_1.py',
    '.venv/Lib/site-packages/django/contrib/auth/migrations/0011_update_proxy_permissions_1.py',
    '.venv/Lib/site-packages/django/contrib/auth/migrations/0012_alter_user_first_name_max_length_1.py'
]

# Remove each file
for file_path in files_to_remove:
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Removed: {file_path}")
        else:
            print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error removing {file_path}: {str(e)}")

print("Done removing duplicate migration files.") 