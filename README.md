# Hearthstone
仿照《炉石传说》的规则实现了其大部分机制

### 测试环境
Python3.7  
Windows 10  

### 配置
```powershell
pip install cocos2d  
pip install flask  
pip install pyautogui  
```  
PS: 在使用pyautogui模拟鼠标点击的时候可能会出现ctype问题，解决方法：  
在pyautogui模块的 _pyautogui_win.py -> _position()   
将 `cursor = POINT()`   
替换为 `cursor = ctypes.wintypes.POINT()` 即可  

### 运行
- 服务端启动 hsServe.server  
- 客户端启动 hsClient.main  

##### 注意
- 由于只有双人对战模式，需启动两个客户端  
- cocos2dx很难用，或者说本人没掌握好，图形界面的操作要慢，很多事件被迫使用模拟鼠标点击来触发，请确保两个客户端窗口的右上角尽量一直显示在屏幕上  

### 基本机制
- 抽牌
- 弃牌
- 召唤
- 攻击
- 死亡

### 关键字
- 冲锋
- 风怒
- 超级风怒
- 嘲讽
- 亡语
- 战吼
- 法术伤害+X
- 过载

### 机制
1. 打出随从  
打出（打出事件）->【战吼/连击】->召唤（召唤事件）->入场->【安装触发器/登记光环/接受光环】  
2. 转移随从控制权  
离场->入场  