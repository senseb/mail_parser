# USE NGINX with reactjs

```
location /{uri} {
   root  {root_dir};   
   _ try_files $uri /demo/index.html;  _
   index  index.html index.htm; 
}
```
