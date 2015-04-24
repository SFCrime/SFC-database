# quick start: postgres + postgis
### install postgres and postgis
```bash
# brew install postgresql
# initdb /usr/local/var/postgres -E utf8

$ brew install postgis --build-from-source
```
### download data
```bash
$ curl https://data.sfgov.org/api/views/tmnf-yvry/rows.csv\?accessType\=DOWNLOAD > sfpd.csv
```
### view data size/rows
```bash
$ du -h sfpd.csv

$ wc -l sfpd.csv 
```
### view header
```bash
$ head -n 1 sfpd.csv | tr "," "\n"
```
### drop unnecessary column
view column to drop
```bash
$ head sfpd.csv | csvcut -c 12
```
filter out column
```bash
$ csvcut -C 12 sfpd.csv > sfpd_v1.csv
```
### start postgres
```bash
$ pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start

# stop
# pg_ctl -D /usr/local/var/postgres stop -s -m fast

# check server status
# pg_ctl -D /usr/local/var/postgres status
```
### create database
```bash
$ createdb 'sfpd'
```
### add postgis
```bash
$ psql sfpd -c 'CREATE EXTENSION postgis;'
```
### create table `crime`
```
sfpd=# CREATE TABLE crime
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
```bash
# drop table
# psql sfpd -c "DROP TABLE crime;"
```
### load csv
```bash
$ psql sfpd -c "COPY crime FROM '/Users/jsemer/code/SFC-mapping/sfpd_v1.csv' WITH DELIMITER ',' CSV HEADER;"
```
### create `geom` column
```bash
$ psql sfpd -c "ALTER TABLE crime ADD COLUMN geom geography;"

# drop column
# psql sfpd -c "ALTER TABLE crime DROP COLUMN geom RESTRICT;"
```
### convert X, Y coordinates to point data type
```bash
$ psql sfpd -c "UPDATE crime SET geom = ST_SetSRID(ST_MakePoint(X, Y), 4326)::geography;"
```
### find points inside polygon
note: first and last coordinates must match; X, Y coordinates in polygon are switched
```bash
# total crimes by year in dolores park
$ psql sfpd -c "SELECT EXTRACT(YEAR FROM date) as year, COUNT(*) FROM crime WHERE ST_Intersects(geom, ST_PolygonFromText('POLYGON((-122.42843270301817 37.761266519836255,-122.42615818977356 37.76139374803265,-122.42584705352783 37.75822994194451,-122.42810010910034 37.75808574380483,-122.42843270301817 37.761266519836255))', 4326)) GROUP BY year ORDER BY year DESC;"
```