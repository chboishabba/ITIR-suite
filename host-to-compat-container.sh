docker exec -it ITIR %command%
create user c if not exists
become c
run %command%
