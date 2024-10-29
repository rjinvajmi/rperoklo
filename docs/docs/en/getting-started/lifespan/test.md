---
# 0.5 - API
# 2 - Release
# 3 - Contributing
# 5 - Template Page
# 10 - Default
search:
  boost: 10
---

# Events Testing

In the most cases you are testing your subscriber/publisher functions, but sometimes you need to trigger some lifespan hooks in your tests too.

For this reason, **FastStream** has a special **TestApp** patcher working as a regular async context manager.

{! includes/getting_started/lifespan/testing.md !}

## Using with **TestBroker**

If you want to use In-Memory patched broker in your tests, it's advisable to patch the broker first (before applying the application patch).

Also, **TestApp** and **TestBroker** are calling `broker.start()` both. According to the original logic, broker should be started in the `FastStream` application, but **TestBroker** applied first breaks this behavior. This reason **TestApp** prevents **TestBroker** `broker.start()` call if it placed inside **TestBroker** context.

This behavior is ruled by `connect_only` **TestBroker** argument. By default it has `None` value, but **TestApp** can set it to `True/False` by inner logic. To prevent this "magic", just setup `connect_only` argument manually.

!!! warning
    With `#!python connect_only=False`, all `FastStream` hooks will be called after **broker was started**, what can breaks some `@app.on_startup` logic.
