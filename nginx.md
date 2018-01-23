# USE NGINX with reactjs

location /{uri} {
   root  {root_dir};   
   <font color=red>_try_files $uri /demo/index.html;  _</font>
   index  index.html index.htm; 
}
