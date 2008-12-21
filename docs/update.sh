tedia2sql -i tietokanta.dia -o tietokanta.sql -t mysql -d
mysql --execute="create database if not exists tupa"
mysql tupa < tietokanta.sql
