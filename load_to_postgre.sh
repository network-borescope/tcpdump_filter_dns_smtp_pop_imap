#!/bin/bash
current_directory=`pwd`
for filename in filtered_data/*.csv; do
    echo "loading $filename to postgre..."
    psql -U borescope -d rnp -c "COPY raw(dt, sip, ttl, ipid, dip, proto, sport, dport, s1, s2, s3, s4, tag, typ, count) from '$current_directory/$filename' DELIMITER '|' CSV HEADER;"
    rm "$current_directory/$filename"
done