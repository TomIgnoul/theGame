PostgreSQL Docker Setup — The Game Project

Project Path
/home/tom/Dev/theGame/

Step 1 — Create the Docker Compose Setup
----------------------------------------
In your project root:
    cd /home/user/Dev/theGame
    nano docker-compose.yml

Paste the following:
----------------------------------------
version: "3.9"

services:
  postgres:
    image: postgres:15
    container_name: thegame-db
    network_mode: "host"
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: W@cthw00rd
      POSTGRES_DB: thegame
    ports:
      - "5432:5432"
    volumes:
      - thegame_data:/var/lib/postgresql/data
    restart: always

volumes:
  thegame_data:

This creates a PostgreSQL container with persistent storage and makes it accessible on port 5432.

Step 2 — Start the Database
---------------------------
Run:
    sudo docker compose up -d

Verify if it is active:
    sudo docker ps

Expected result:
IMAGE        | PORTS                   | NAMES
postgres:15  | 0.0.0.0:5432->5432/tcp  | thegame-db

Step 3 — Connect to the Database
--------------------------------
Connect via Docker:
    sudo docker exec -it thegame-db psql -U admin -d thegame

If successful, you will see:
    thegame=#

You can run:
    \l          -- list databases
    \dt         -- list tables
    SELECT NOW();  -- test query
    \q          -- quit

Step 4 — Optional GUI Connection
--------------------------------
You can also connect using pgAdmin, DBeaver, or TablePlus.

Setting   | Value
Host      | localhost
Port      | 5432
Database  | thegame
User      | admin
Password  | W@cthw00rd

Summary
-------
You now have a working PostgreSQL 15 container managed via Docker Compose:
- Database: thegame
- User: admin
- Persistent volume: thegame_data
- Accessible at: localhost:5432
