# USE NGINX with reactjs

```
location /{uri_dir} {
   root  {root_dir};   
   try_files $uri /{uri_dir}/index.html;
   index  index.html index.htm; 
}
```
