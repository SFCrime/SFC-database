# quick start: db

Relevant Documentation:
- [Geograph Basics](http://postgis.net/docs/using_postgis_dbmanagement.html#Geography_Basics)
- [ST_MakePoint](http://postgis.net/docs/ST_MakePoint.html)

Terminology
- Event = Hypernym (e.g. Bay To Breakers)
- Event Instance = Hyponym (e.g. Bay To Breakers 2014)

## install postgres and postgis for OSX
At times this install may fail on OSX. Be sure to install that specific dependency manually.
```bash
$ brew install postgresql
$ initdb /usr/local/var/postgres -E utf8
$ brew install postgis --build-from-source
```

## download data
```bash
$ curl https://data.sfgov.org/api/views/tmnf-yvry/rows.csv\?accessType\=DOWNLOAD > sfpd.csv
```

## data size
```bash
$ du -h sfpd.csv
342M    sfpd.csv
```

## row count
```bash
$ wc -l sfpd.csv
1747840 sfpd.csv
```

## view header
```bash
$ head -n 1 sfpd.csv | tr "," "\n"
IncidntNum
Category
Descript
DayOfWeek
Date
Time
PdDistrict
Resolution
Address
X
Y
Location
PdId
```

## drop unnecessary csv column
view column to drop
```bash
$ head sfpd.csv | csvcut -c 12
Location
"(37.7695298789096, -122.414126305537)"
"(37.7695298789096, -122.414126305537)"
"(37.7828276498838, -122.409708423721)"
"(37.7828276498838, -122.409708423721)"
"(37.7324323864471, -122.391522893042)"
"(37.7324323864471, -122.391522893042)"
"(37.7324323864471, -122.391522893042)"
"(37.7717499829743, -122.437022956853)"
"(37.761644197745, -122.412051228021)"
```

filter out column
```bash
$ csvcut -C 12 sfpd.csv > sfpd_v1.csv
```

## start postgres
```bash
$ pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start
```

stop postgres
```bash
$ pg_ctl -D /usr/local/var/postgres stop -s -m fast
```

check server status
```bash
$ pg_ctl -D /usr/local/var/postgres status
```

## create user
```bash
$ createuser info247 --pwprompt --interactive
```

```
Enter password for new role: test
Enter it again: test
Shall the new role be a superuser? (y/n) y
Shall the new role be allowed to create databases? (y/n) y
Shall the new role be allowed to create more new roles? (y/n) n
```

## create database
```bash
$ createdb -O 'info247' sfpd
```

drop database
```bash
$ dropdb 'crime'
```

## login to psql
```bash
$ psql sfpd info247
```

```
sfpd=# \du
List of roles
Role name |                   Attributes                   | Member of
-----------+------------------------------------------------+-----------
info247   | Superuser, Create DB                           | {}
jsemer    | Superuser, Create role, Create DB, Replication | {}
```

## add postgis
only superusers can create postgis extension

```sql
CREATE EXTENSION postgis;
```

## create table `crime`
```
CREATE TABLE crime
(
 IncidntNum bigint,
 Category varchar,
 Descript varchar,
 DayOfWeek varchar,
 Date date,
 Time time,
 PdDistrict varchar,
 Resolution varchar,
 Address varchar,
 X double precision,
 Y double precision,
 PdId bigint
 );
```

drop table
```sql
DROP TABLE crime;
```

## load csv
```sql
COPY crime FROM '/Users/jsemer/code/SFC-database/sfpd_v1.csv' WITH DELIMITER ',' CSV HEADER;
```

## create `geom` column
```sql
ALTER TABLE crime ADD COLUMN geom geography;
```
drop column
```sql
ALTER TABLE crime DROP COLUMN geom RESTRICT;
```

## convert X, Y coordinates to `geography` data type
X is longitude and Y is latitude (see [documentation](http://postgis.net/docs/ST_MakePoint.html))

```sql
UPDATE crime SET geom = ST_SetSRID(ST_MakePoint(X, Y), 4326)::geography;
```

## find points inside polygon
(note: first and last coordinates must match; X, Y coordinates in polygon are switched)

total crimes by year in dolores park

```sql
SELECT EXTRACT(YEAR FROM date) as year, COUNT(*) FROM crime WHERE ST_Intersects(geom, ST_PolygonFromText('POLYGON((-122.42843270301817 37.761266519836255,-122.42615818977356 37.76139374803265,-122.42584705352783 37.75822994194451,-122.42810010910034 37.75808574380483,-122.42843270301817 37.761266519836255))', 4326)) GROUP BY year ORDER BY year DESC;
```

```
year | count
------+-------
2015 |    54
2014 |   165
2013 |   298
2012 |   195
2011 |   148
2010 |   138
2009 |   128
2008 |   113
2007 |   120
2006 |    97
2005 |   132
2004 |   119
2003 |   105
(13 rows)
```

total crimes by year in golden gate park
```sql
SELECT EXTRACT(YEAR FROM date) as year, COUNT(*) FROM crime WHERE ST_Intersects(geom, ST_PolygonFromText('POLYGON((-122.51103401184083 37.771393199665255, -122.46597290039062 37.77356423357254, -122.45455741882324 37.774785412131244, -122.45301246643065 37.76637243960179, -122.45738983154297 37.76589748519095, -122.45867729187012 37.7662367386528, -122.51026153564452 37.7641333421029, -122.51103401184083 37.771393199665255))', 4326)) GROUP BY year ORDER BY year DESC;
```

```
year | count
------+-------
2015 |   579
2014 |  2004
2013 |  1889
2012 |  1707
2011 |  1373
2010 |  1498
2009 |  1957
2008 |  1544
2007 |  1624
2006 |  1294
2005 |  1136
2004 |  1323
2003 |  1515
(13 rows)
```


# quick start: api
## start flask app

```bash
$ mkvirtualenv crime

$ python -V
Python 3.4.2

$ pip install -r requirements.txt

$ chmod a+x app.py

$ ./app.py
```

## use api
view crimes by category in dolores park
```bash
$ curl -i 'http://localhost:5000/api/v1/polygon/%2D122.42841124534607%2037.76128348360843%2C%2D122.42810010910034%2037.7580942260561%2C%2D122.42584705352783%2037.75822145970878%2C%2D122.42613673210143%2037.76141071177564%2C%2D122.42841124534607%2037.76128348360843'
```

##Adding Events Table
```sql
CREATE TYPE shapes as ENUM ('point', 'polygon', 'line');

CREATE TABLE events (
    id_name varchar(255) PRIMARY KEY,
    name varchar(250),
    year integer,
    start_date date,
    start_time time without time zone,
    end_date date,
    end_time time without time zone,
    shape_type shapes,
    shape geometry
    );
```

## Adding the first Event
```sql
INSERT INTO events (id_name, name,year ,start_date ,start_time ,end_date ,end_time, shape_type, shape) VALUES ('hardly-strictly-2014', 'Hardly Strictly',2014,'10/3/2014','10:30AM','10/5/2014','07:00PM','polygon', ST_PolygonFromText('POLYGON((-122.51103401184083 37.771393199665255, -122.46597290039062 37.77356423357254, -122.45455741882324 37.774785412131244, -122.45301246643065 37.76637243960179, -122.45738983154297 37.76589748519095, -122.45867729187012 37.7662367386528, -122.51026153564452 37.7641333421029, -122.51103401184083 37.771393199665255))', 4326));
```

