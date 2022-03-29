## 文件目录

+ `build/`和`dist/`是pyinstaller生成的，打包好的软件在`dist/`目录下
+ `awaken/`和`msc/`是和语音唤醒相关的资源
+ `scripts/`是python脚本文件
+ `data/`是一些数据文件
+ `rcc/`是一些资源文件（图片Resource）
+ `Carbon.ico`是图标
+ `CarbonUI.spec`是pyinstaller生成的
+ `Resource.qrc`是qt的Resource文件
+ `Resource_rc.py`是PyRcc生成的写入二进制资源的python脚本



## 软件功能

#### 1. 唤醒

+ 双击UI唤醒

	鼠标双击UI，即可唤醒录音，若检测到一段时间未接收到声音，自主结束录制并分析语音并执行相应功能

	![Carbon](README.assets/Carbon.gif)

+ ##### 语音唤醒

	使用`”卡布卡布“`进行语音唤醒，即可唤醒聆听功能

#### 2. 语音识别

+ 调用百度语音识别接口，将接收到的录音进行`语音-->文字`的转换

#### 3. 功能执行

​		根据语音输入内容，进行相应的功能执行

+ 关于PC的操作
	+ 关机
	+ 锁屏
+ 打开电脑端的软件
+ 浏览器相关操作
	+ 百度搜索`语音输入的关键词`
	+ 一些其他网页的搜索
	+ 利用==**爬虫**==技术，根据输入的音乐名称，使用网易云的网页端进行播放
+ 微信相关操作
	+ 打开微信，根据语音输入，给**某人**发送**某段消息**
	+ 打开微信朋友圈
+ 网易云音乐相关操作
	+ 有关音乐的一系列操作：播放、暂停、上一首、下一首、音量、歌词显示
+ TODO: 等待补充
