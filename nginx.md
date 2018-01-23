# USE NGINX with reactjs

```
location /{uri} {
   root  {root_dir};   
   try_files $uri /demo/index.html;
   index  index.html index.htm; 
}
```
