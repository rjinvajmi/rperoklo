---
# 0.5 - API
# 2 - Release
# 3 - Contributing
# 5 - Template Page
# 10 - Default
search:
  boost: 10
# template variables
note_decor: Now you can use the created router to register handlers and publishers as if it were a regular broker
note_include: Then you can simply include all the handlers declared using the router in your broker
note_publish: Please note that when publishing a message, you now need to specify the same prefix that you used when creating the router
---

# Broker Router

Sometimes you want to:

* split an application into includable modules
* separate business logic from your handler registration
* apply some [decoder](../serialization/index.md)/[middleware](../middlewares/index.md)/[dependencies](../dependencies/global.md) to a subscribers group

For these reasons, **FastStream** has a special *Broker Router*.

## Router Usage

First, you need to import the *Broker Router* from the same module from where you imported the broker.

!!! note ""
    When creating a *Broker Router*, you can specify a prefix that will be automatically applied to all subscribers and publishers of this router.

{% import 'getting_started/routers/1.md' as includes with context %}
{{ includes }}

!!! tip
    Also, when creating a *Broker Router*, you can specify [middleware](../middlewares/index.md), [dependencies](../dependencies/index.md#top-level-dependencies), [parser](../serialization/parser.md) and [decoder](../serialization/decoder.md) to apply them to all subscribers declared via this router.

## Delay Handler Registration

If you want to separate your application's core logic from **FastStream**'s routing logic, you can write some core functions and use them as *Broker Router* `handlers` later:

{! includes/getting_started/routers/2.md !}

!!! warning
    Be careful, this way you won't be able to test your handlers with a [`mock`](../subscription/test.md) object.
