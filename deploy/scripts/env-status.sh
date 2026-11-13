#!/bin/bash
# ============================================================
# 医药分析系统：只查状态，不动任何进程
#
#   用法：bash /opt/env-status.sh
#
# 适合快速判断"现在系统是好的还是坏的"，几秒出结果。
# ============================================================
set -u
MYPASS=123456
ok()  { printf '  \033[32m[ OK ]\033[0m %s\n' "$1"; }
bad() { printf '  \033[31m[FAIL]\033[0m %s\n' "$1"; }
port_up() { ss -lnt 2>/dev/null | grep -q ":$1 "; }

echo ""
echo "===== 服务端口 ====="
for pair in "2181:ZooKeeper" "9000:HDFS" "8088:YARN" "16010:HBase" \
            "9083:HiveMetastore" "7070:Kylin" "3306:MySQL" "83:后端接口" "8000:大屏"; do
  p=${pair%%:*}; n=${pair##*:}
  if port_up $p; then ok "$n ($p)"; else bad "$n ($p) 未监听"; fi
done

echo ""
echo "===== 数据 ====="
ROWS=$(mysql -uroot -p$MYPASS -N -B -e "SELECT COUNT(*) FROM yiyao.prescription_diseases;" 2>/dev/null)
[ "$ROWS" = "1000000" ] && ok "MySQL 处方表 $ROWS 行" || bad "MySQL 处方表行数 ${ROWS:-取不到}"

DIRS=$(hdfs dfs -ls /bi_data/mysql 2>/dev/null | grep -c '^d')
[ "$DIRS" = "6" ] && ok "HDFS /bi_data/mysql 6 个目录" || bad "HDFS 目录数 ${DIRS:-0}（期望 6）"

IDX=$(mysql -uroot -p$MYPASS -N -B yiyao -e "SELECT COUNT(DISTINCT INDEX_NAME) FROM information_schema.STATISTICS WHERE TABLE_SCHEMA='yiyao' AND INDEX_NAME LIKE 'idx_%';" 2>/dev/null)
[ "$IDX" = "9" ] && ok "MySQL 自定义索引 9 个" || bad "MySQL 自定义索引 ${IDX:-0} 个（期望 9）"

echo ""
echo "===== 接口与大屏 ====="
CODE=$(curl -s -o /dev/null -w '%{http_code}' --max-time 120 http://localhost:83/home/overview 2>/dev/null)
[ "$CODE" = "200" ] && ok "后端 /home/overview 200" || bad "后端 /home/overview HTTP=$CODE"

CODE=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 http://localhost:83/ 2>/dev/null)
[ "$CODE" = "200" ] && ok "前端页面 / 200" || bad "前端页面 / HTTP=$CODE"

HEALTH=$(curl -s --max-time 30 http://localhost:8000/api/health/ 2>/dev/null)
case "$HEALTH" in
  *'"db": true'*)  ok "大屏 db: true" ;;
  *)               bad "大屏健康检查：${HEALTH:-无响应}" ;;
esac

IP=$(hostname -I | awk '{print $1}')
echo ""
echo "访问地址： http://$IP:83/    大屏： http://$IP:8000/"
echo ""
