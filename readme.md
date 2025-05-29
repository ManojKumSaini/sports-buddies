# Sports Buddies Plugin

A matching plugin to help people find others with similar sports interests.

## Features
- Match users based on their preferred sports and location
- Seamlessly integrates with your existing application
- Common swipe-right interaction to connect with others
- Simple and user-friendly interface

---

## Step 1 – Create a Virtual Environment

**For macOS users:**

```bash
uv venv
source .venv/bin/activate
uv pip compile requirements.in > requirements.txt
uv pip install -r requirements.txt
```

---

## Step 2 – Log in to DBVisualizer with Your Credentials

- Change your password by running the following SQL command on the `who_am_i_data_sink` database:

```sql
ALTER USER your_user_name PASSWORD 'new_password';
```

- After that, you should have access to the database.

---

## Step 3 – Create a Data Folder (Ignored by Git)

This folder is required to store local configuration and will **not** be pushed to GitHub due to `.gitignore`.

**For macOS users:**

```bash
mkdir data
```

Then, create a `config.txt` file inside that folder with your connection details
**please change the ipm port number user and password to your data**:

```bash
echo host=your_host_ip > data/config.txt
echo port=your_port_number >> data/config.txt
echo database=who_am_i_data_sink >> data/config.txt
echo user=your_username >> data/config.txt
echo password=your_password >> data/config.txt
```

*Ask Dave for the correct IP, port, and credentials.*

---

## Step 4 – Create a New User

Run the following Python script:

```bash
python 01_new_user.py
```

This will open a **Tkinter input form**:

![tkinter](images/tkinterface_user.png)

- Pressing **Submit** will save the user information **locally** (and only locally) in your `data` folder.
- A **hashed user ID** will be generated and saved alongside the personal data in `secret_info.csv`:

![secret_info](images/secret_info_csv.png)

- Finally, a new entry will be added to the **`users` table** in the `who_am_i_data_sink` database.  
  This includes:
  - a new `user_number`
  - the hashed `user_id`
  - a `creation_time` timestamp

![DB](images/DB_users.png)
