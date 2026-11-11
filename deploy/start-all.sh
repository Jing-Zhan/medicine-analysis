#!/bin/bash
# 集群启动脚本 — 依据下发材料「医药环境启动」整理
# 用法：bash start-all.sh
# 关闭：按反向顺序执行 stop-hbase.sh、stop-all.sh、zkServer.sh stop、kylin.sh stop

set -u

echo "=============================================="
echo " 目标适应症及用药数据分析系统 — 集群启动"
echo "=============================================="

ZK_HOME=${ZK_HOME:-/opt/module/zookeeper}
HADOOP_HOME=${HADOOP_HOME:-/opt/module/hadoop}
HBASE_HOME=${HBASE_HOME:-/opt/module/hbase}
HIVE_HOME=${HIVE_HOME:-/opt/module/hive}
KYLIN_HOME=${KYLIN_HOME:-/opt/module/kylin}

echo ""
echo "[1/6] 检查 /etc/hosts"
getent hosts master >/dev/null && echo "      master 解析正常" || echo "      [警告] master 解析异常，检查 /etc/hosts"
ping -c 1 -W 2 slave1 >/dev/null 2>&1 && echo "      slave1 可达" || echo "      [警告] slave1 不可达"

echo ""
echo "[2/6] 启动 ZooKeeper（全部节点执行本脚本时均会启动）"
$ZK_HOME/bin/zkServer.sh start

echo ""
echo "[3/6] 启动 HDFS 与 YARN（仅 master）"
if [ "$(hostname)" = "master" ]; then
  $HADOOP_HOME/sbin/start-all.sh
  $HADOOP_HOME/sbin/mr-jobhistory-daemon.sh start historyserver
else
  echo "      当前节点非 master，跳过"
fi

echo ""
echo "[4/6] 启动 HBase（仅 master）"
if [ "$(hostname)" = "master" ]; then
  $HBASE_HOME/bin/start-hbase.sh
else
  echo "      当前节点非 master，跳过"
fi

echo ""
echo "[5/6] 启动 Hive 服务"
nohup $HIVE_HOME/bin/hive --service metastore >/tmp/hive-metastore.log 2>&1 &
nohup $HIVE_HOME/bin/hive --service hiveserver2 >/tmp/hive-hiveserver2.log 2>&1 &
echo "      metastore 与 hiveserver2 已在后台启动，日志见 /tmp/hive-*.log"

echo ""
echo "[6/6] 启动 Kylin（仅 master，需 HBase 与 Hive 就绪）"
if [ "$(hostname)" = "master" ]; then
  $KYLIN_HOME/bin/kylin.sh start
else
  echo "      当前节点非 master，跳过"
fi

echo ""
echo "=============================================="
echo " 进程检查（jps）"
echo "=============================================="
jps

echo ""
echo " Web 入口（将 <ip> 替换为 master 内网 IP）"
echo "   HDFS     http://<ip>:50070/"
echo "   YARN     http://<ip>:8088/"
echo "   HBase    http://<ip>:60010/"
echo "   Kylin    http://<ip>:7070/kylin   （ADMIN / KYLIN）"
echo "=============================================="
echo " 关闭顺序：kylin.sh stop → stop-hbase.sh → stop-all.sh → zkServer.sh stop"
echo "=============================================="
