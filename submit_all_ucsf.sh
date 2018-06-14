#!/bin/bash
ID=131cf62d-ad78-49c1-a699-5bcc1004cd12 make zero
ID=2fbc25da-3965-49c4-866f-72cf0abc2417 make zero
ID=940171e7-d358-463a-8d9a-2b2fa90c2a84 make zero
ID=c2e2e081-4c39-4201-8a27-7b469ed39490 make zero
ID=c7dbcfac-37ea-43f8-8899-1a9f2fb56341 make zero
ID=ccc2ba97-912f-4b62-b767-cca129ee6a56 make zero
ID=cf11c31c-f4c3-48ba-9c46-66f406d0b7a1 make zero
ID=db2d85aa-4f94-4e77-8755-6b94a710c1aa make zero
ID=ec3d977b-c310-4df3-a444-f79bc3dd8b58 make zero
ID=ef5c3164-6f45-4d3a-88f0-4509226c5571 make zero
ID=f0314175-2d19-4146-8754-fc5aed3ab420 make zero
ID=f9b6a782-bbf5-4be8-bf7e-d1a9586d9552 make zero

docker exec -it cgtd_cgtd_1 python submit.py \
  --fields submissions/db2d85aa-4f94-4e77-8755-6b94a710c1aa/1/fields.json \
  --files `find submissions/db2d85aa-4f94-4e77-8755-6b94a710c1aa/1/files -type f -name '*.dcm'`

docker exec -it cgtd_cgtd_1 python submit.py \
  --fields submissions/db2d85aa-4f94-4e77-8755-6b94a710c1aa/2/fields.json \
  --files `find submissions/db2d85aa-4f94-4e77-8755-6b94a710c1aa/2/files -type f -name '*.dcm'`
