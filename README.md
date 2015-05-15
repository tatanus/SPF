# speedphish
tool to speed up the creation and execution of a standard phishing exercise

## Testing

### Web: Virtual Hosts 

```
"edit /etc/hosts" to include:
127.0.0.1	citrix.example.com
127.0.0.1	owa.example.com
127.0.0.1	office365.example.com

cd src
python spf.py --test -d example.com

or to just test the websites:
cd src
python web.py default.cfg
```

then open a web browser to:

```
to test vhosts:
citrix.example.com
office365.example.com
owa.example.com

to test them as seperate web ports:
127.0.0.1:8000
127.0.0.1:8001
127.0.0.1:8002
```

and entered credentials will be logged to:

```
citrix.log
office365.log
owa.log
```
