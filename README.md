## Description
根据[WeixinBot](https://github.com/Urinx/WeixinBot)这个项目，
还有[WEB版微信协议部分功能分析](http://blog.csdn.net/wonxxx/article/details/51787041)这篇文章里提供的微信操作流程编写。
修正了他们一些错误，比如*WeixinBot*里请求缺少了部分参数，或者时间戳不正确（虽然貌似没什么影响），
比如*WEB版微信协议部分功能分析*里使用的*ContactFlag*这个字段并不能有效区分各类账号，*WeixinBot*里用的*VerifyFlag*看起来更准确但作者的分类有些错误。。。
当然，写这个主要是添加把微信消息保存到本地的功能。。。
时间有限，加上自己也没有对web微信的各个实现细节去一一研究和实践，所以会有很多细节处理的比较粗糙或者有误，最关键的是。。。说不定哪一天TX的人改了一点点就不好用了~

...还有一大半没写好...working...