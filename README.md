# BUAA课表写入日历
北航研究生课表导入日历，提供全平台支持

### 移动端效果图
![移动端效果图](/html_root/static/classtable.png)
### PC端效果图
![Win10效果图](/html_root/static/img/win10_4.png)

## 部署
1. 编辑`server/setting.py`, 配置七牛云和学期开始时间
2. 全局替换 `html_root` 文件夹下的文件，将 `static.wecqu.com` 替换成你的七牛云域名，将`buaa.wecqu.com`替换成服务器ip/域名
3. 安装依赖
`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt`
4. 运行
`python -m server.run --port=5000`

或直接使用Docker部署(依然需要前两步)：
```
docker build -t buaa .
docker run --name buaa_schedule -v `pwd`:/usr/src/app/ -p 127.0.0.1:5000:5000 -d buaa python3 -m server.run --port=5000
```
