# BUAA课表写入日历教程
本教程可将您的课表导入到系统日历中，可以方便地查看课表，无需安装任何软件（安卓平台可能需要一个导入工具），并支持上课提醒。

### 移动端效果图
![移动端效果图](./static/classtable.png)
### PC效果图
![Win10效果图](./static/img/win10_4.png)

## 使用方法
电脑端使用Chrome打开课表页面，按下F12打开Chrome调试面板，在`console`栏中粘贴以下代码，并按下回车执行。
```js
var request = new XMLHttpRequest();
request.open('POST', 'http://buaa.wecqu.com/api/ics', true);
request.onload = function() {
  if (this.status >= 200 && this.status < 400) {
    var data = JSON.parse(this.response);
    if(!data.status)
        alert(data.message);
    else
        window.open('http://buaa.wecqu.com/result.html?key='+data.data);
  }
};
request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
request.send('data='+encodeURIComponent(document.getElementsByClassName('Timetable-content')[0].innerHTML));

```

之后根据页面提示进行操作。

## 关于本项目
### 反馈
邮件 `wang0.618&qq.com` (将&替换成@)
### 隐私相关
本项目需要将您的课表数据保存至服务器端，但课表数据中不包含您的身份信息，不会造成隐私泄露。
### 项目代码
项目已在github开源: [https://github.com/wang0618](https://github.com/wang0618)