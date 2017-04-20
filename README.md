# quote-bot

A Telegram Bot for Managing Quotes

思路：

Public Channel的对话是有对应的URL的。即ChannelURL/<id>的形式，如https://t.me/Y2xhcmt6ancncyBwZXJzb25hbCBjaGFu/7

所以首先要把语录Channel中的每条消息以及对应的URL先存起来，然后用户查询的时候对消息进行全文检索。bot返回消息的URL。

如果直接在与其他用户的对话中使用bot进行inline查询，那么点击后直接发出了语录的URL。这样是不合适的。

所以可以引导用户与bot私聊进行查询。这样就不需要inline了。在与bot私聊界面返回对应的URL，然后用户点击跳转到对应的语录消息，然后转发出来即可。

也可以支持搜索某个用户的所有语录消息。反正Telegram有链接的预览。但是如果某个用户的所有语录消息的数量太多，全部返回给用户显然是不合适的，因此可以分页。

改进：

以后，用户依然转发消息到原来的语录中。然后bot监听语录中的消息（因此bot需要被加入到Channel中），遇到新的消息加入到数据库中。

当然，也可以做一些统计。如语录中谁的消息最多，谁转发的最多，哪条消息被查询的次数最多，哪个用户查询的次数最多，等等。

由于似乎Private Channel无法以ChannelURL+ID的形式访问消息，所以语录Channel必须是Public的。那么对于bot的使用是否有必要进行认证？如何认证？
