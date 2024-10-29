---
# 0.5 - API
# 2 - Release
# 3 - Contributing
# 5 - Template Page
# 10 - Default
search:
  boost: 10
---

# Broker Publishing

The easiest way to publish a message is to use a Broker, which allows you to use it as a publisher client in any applications.

In the **FastStream** project, this call is not represented in the **AsyncAPI** scheme. You can use it to send rarely-publishing messages, such as startup or shutdown events.

{! includes/getting_started/publishing/broker/1.md !}
