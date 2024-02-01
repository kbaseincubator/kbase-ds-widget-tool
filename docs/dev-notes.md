## Debugging http info

Sometimes it is useful to know what information the server has about the http
connection. This set of changes augments the "status" method to provide it.

in server, below:

```python
    ctx = MethodContext(self.userlog)
```

add

```python
   whitelist_keys = [
            "REQUEST_METHOD",
            "REQUEST_URI",
            "PATH_INFO",
            "QUERY_STRING",
            "SERVER_PROTOCOL",
            "SCRIPT_NAME",
            "SERVER_NAME",
            "SERVER_PORT",
            "UWSGI_ROUTER",
            "REMOTE_ADDR",
            "REMOTE_PORT",
            "HTTP_HOST",
            "CONTENT_LENGTH",
            "HTTP_PRAGMA",
            "HTTP_CACHE_CONTROL"
        ]
        ctx['environ'] = [(key, value) for (key, value) in environ.items() if key in whitelist_keys]
        ctx['environ_omitted'] = [key for key in environ.keys() if key not in whitelist_keys]
```

In the impl file, add this context to the status handler:

```python
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'environ': ctx.get('environ'),
                     'environ_omitted': ctx.get('environ_omitted'),
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
        #END_STATUS
        return [returnVal]
```



To apply this to the server, you should keep a copy of the server file next to the
generated one, and swap it out in the compile task of the Makefile.

e.g. 

```Makefile
compile:
	kb-sdk compile $(SPEC_FILE) \
		--out $(LIB_DIR) \
		--pysrvname $(SERVICE_CAPS).$(SERVICE_CAPS)Server \
		--pyimplname $(SERVICE_CAPS).$(SERVICE_CAPS)Impl;
	# cheap server fix
	cp lib/eapearsonWidgetDemo3/eapearsonWidgetDemo3Server-ds.py lib/eapearsonWidgetDemo3/eapearsonWidgetDemo3Server.py
```