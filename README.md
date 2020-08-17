
```
LDFLAGS=`echo $(pg_config --ldflags)` pip install psycopg2
```

```
pip freeze > requirements.txt
```


```
docker build -t productor_app_basis --file ./DockerfileAppBasis .
docker tag productor_app_basis:latest fdrennan/productor_app:latest
docker push fdrennan/productor_app:latest
```# DL-Tools
# DL-Tools
# ec2_ml
