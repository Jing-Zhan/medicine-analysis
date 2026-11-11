# 部署说明

## 一、集群启动

```bash
bash deploy/start-all.sh
```

顺序：`/etc/hosts` → ZooKeeper → HDFS/YARN → HBase → Hive → Kylin。

关闭时反向执行：

```bash
$KYLIN_HOME/bin/kylin.sh stop
$HBASE_HOME/bin/stop-hbase.sh
$HADOOP_HOME/sbin/stop-all.sh
$ZK_HOME/bin/zkServer.sh stop
```

**Kylin 必须在 HBase 之后启动**，否则元数据读取失败。

## 二、后端部署

```bash
# 本地打包
mvn clean package -DskipTests

# 上传 jar 到 master
# /home/yiyao-0.0.1-SNAPSHOT.jar

# 启动
nohup java -Xms2g -Xmx2g -jar /home/yiyao-0.0.1-SNAPSHOT.jar > /home/yiyao.log 2>&1 &

# 验证
curl http://localhost:83/home/citylevel
```

端口为 `83`，与前端 `src/config.js` 的 `baseUrl` 对应。

## 三、前端部署

```bash
npm run build            # 产出 dist/
# 上传 dist 到 master 的 /home/dist

# 放入 Tomcat
cp -r /home/dist/ /opt/module/apache-tomcat-8.5.85/webapps/ROOT/
/opt/module/apache-tomcat-8.5.85/bin/startup.sh
```

访问 `http://<ip>:8080/dist`。

路由为 hash 模式，`/dist/#/home` 可正常刷新。

## 四、大屏部署

```bash
# 服务器安装 Python 3.9（源码编译约 20—40 分钟）
tar -zxvf Python-3.9.10.tgz -C /opt/python
cd /opt/python/Python-3.9.10
./configure --prefix=/usr/local/python3.9 --with-ssl
make && make install
ln -s /usr/local/python3.9/bin/python3.9 /usr/local/bin/python3

# 安装依赖
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 启动
cd /home/medicine
python3 manage.py runserver 0.0.0.0:8000
```

### 已知问题：sqlite3 版本过低

报错 `django.db.utils.NotSupportedError: deterministic=True requires SQLite 3.8.3`。

处理方式：

```bash
pip3 install pysqlite3 pysqlite3-binary
# 编辑 /usr/local/python3.9/lib/python3.9/site-packages/django/db/backends/sqlite3/base.py
# 注释 from sqlite3 import dbapi2 as Database
# 改为 from pysqlite3 import dbapi2 as Database
```

## 五、部署检查清单

| 检查项 | 命令 / 方式 | 结果 |
| --- | --- | --- |
| 集群进程 | `jps` | |
| HDFS | `http://<ip>:50070/` | |
| YARN | `http://<ip>:8088/` | |
| HBase | `http://<ip>:60010/` | |
| Kylin | `http://<ip>:7070/kylin` | |
| 后端接口 | `curl http://localhost:83/home/age` | |
| BI 系统 | `http://<ip>:8080/dist` | |
| 大屏 | `http://<ip>:8000` | |

## 六、演示当天

答辩前 30 分钟完成：

1. 启动集群（`start-all.sh`），确认 `jps` 进程齐全
2. 启动后端 jar，`curl` 验证 83 端口
3. 启动 Tomcat（若未开机自启）
4. 启动 Django
5. 浏览器打开两个系统，逐个点一遍图表
