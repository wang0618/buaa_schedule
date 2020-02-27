# BUAA课表写入日历教程
本教程可将您的课表导入到系统日历中，可以方便地查看课表，无需安装任何软件（安卓平台可能需要一个导入工具），并支持上课提醒(win10平台暂不支持提醒功能)。

### 移动端效果图
![移动端效果图](./static/classtable.png)
### PC效果图
![Win10效果图](./static/img/win10_4.png)

## 使用方法
整个操作大约只花费1~2分钟，需要在电脑端进行操作，请按照下方说明进行。

### 0. 在电脑端打开本页面 (https://buaa.wecqu.com)

### 1. 在电脑端使用Chrome浏览器(或Edge浏览器)打开课表页面
访问 `http://gsmis.buaa.edu.cn/`, 选择“查看课表”

### 2. 设置提醒时间和更改课程上课地点
<div onclick="set_alarm(this)" class="btn">设置提醒时间</div> <div onclick="set_trans(this)" class="btn">更改课程上课地点</div> <div class="clearfix"></div> <div id="new_address"></div>

 - 设置提醒时间仅支持IOS平台课表的导入，其他平台请在课表提交后进行设置。
 - 若您的上课地点没有变化，则无需更改课程上课地点

### 3. 提交课表
在课表页面下按`F12`打开浏览器调试面板，在`Console`栏(Edge浏览器中为`控制台`栏)中粘贴以下代码，并按下回车执行。之后根据页面提示选择导入不同平台。
```js
var request = new XMLHttpRequest();
request.open('POST', 'http://buaa.wecqu.com/api/ics', true);
request.onload = function() {
  if (this.status >= 200 && this.status < 400) {
    var data = JSON.parse(this.response);
    if(!data.status) alert(data.message);
    else window.open('http://buaa.wecqu.com/result.html?key='+data.data);
  }
};
request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
var trans = "DEFAULT_TRANS", alarm_minute="DEFAULT_ALARM";
request.send('alarm_minute='+alarm_minute+'&trans='+trans+'&data='+encodeURIComponent(document.getElementsByClassName('Timetable-content')[0].innerHTML)+'&f='+window.location.hash.substr(2,10));

```
<div onclick="copy_code(this)" class="btn">点此复制以上代码</div> <div class="clearfix"></div>

> 在Edge浏览器中回车执行代码后，需要在页面上选择允许弹出窗口。 

![在Console栏中粘贴代码](./static/img/console.png)


## 关于本项目
### 反馈
邮件 `wang0.618&qq.com` (将&替换成@)
### 隐私相关
本项目需要将您的课表数据保存至服务器端，但课表数据中不包含您的身份信息，不会造成隐私泄露。
### 项目代码
项目已在github开源: [https://github.com/wang0618/buaa_schedule](https://github.com/wang0618/buaa_schedule)