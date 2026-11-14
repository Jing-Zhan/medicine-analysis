#!/bin/bash
# ============================================================
# 医药分析系统：一键拉起全部服务 + 自检
#
#   用法：bash /opt/start-all.sh
#
# 做三件事：
#   1. 集群没起来就调 /opt/start-cluster.sh；已经在跑就跳过
#   2. 后端 83 和大屏 8000 没起来就拉起来，起来就跳过
#   3. 全部起完后跑一遍自检，逐项打印 OK / FAIL
#
# 可反复执行，不会重复启动进程。
# ============================================================
set -u

APP_DIR=/home/medicine-analysis
JAR=$APP_DIR/backend/yiyao/target/yiyao-0.0.1-SNAPSHOT.jar
SCREEN_DIR=$APP_DIR/screen
MYPASS=123456
FAILED=0

ok()   { printf '  \033[32m[ OK ]\033[0m %s\n' "$1"; }
bad()  { printf '  \033[31m[FAIL]\033[0m %s\n' "$1"; FAILED=1; }
step() { printf '\n\033[36m== %s ==\033[0m\n' "$1"; }

# 端口是否在监听（$1 端口号）
port_up() { ss -lnt 2>/dev/null | grep -q ":$1 "; }

# 等某个 URL 返回 200，最多等 $2 秒
wait_http() {
  local url=$1 limit=${2:-90} i=0
  while [ $i -lt $limit ]; do
    if [ "$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "$url")" = "200" ]; then
      return 0
    fi
    sleep 3; i=$((i + 3))
    printf '.'
  done
  echo ""
  return 1
}

# ------------------------------------------------------------ 1. 集群
step "1/5 集群：ZooKeeper / HDFS / YARN / HBase / Hive metastore / Kylin"
need_cluster=0
for p in 2181 9000 8088 16010 9083 7070; do
  port_up $p || need_cluster=1
done
if [ $need_cluster -eq 0 ]; then
  ok "6 个组件端口全部在监听，跳过启动"
else
  echo "  有组件没起来，执行 /opt/start-cluster.sh（约 1~3 分钟）……"
  bash /opt/start-cluster.sh > /tmp/start-cluster.log 2>&1
  echo "  完整日志：/tmp/start-cluster.log"
fi
for pair in "2181:ZooKeeper" "9000:HDFS" "8088:YARN" "16010:HBase" "9083:HiveMetastore" "7070:Kylin"; do
  p=${pair%%:*}; n=${pair##*:}
  if port_up $p; then ok "$n ($p)"; else bad "$n ($p) 未监听"; fi
done

# ------------------------------------------------------------ 2. MySQL
step "2/5 MySQL"
if ! port_up 3306; then
  echo "  启动 mysqld……"
  systemctl start mysqld 2>/dev/null || service mysqld start 2>/dev/null
  sleep 8
fi
if port_up 3306; then
  ROWS=$(mysql -uroot -p$MYPASS -N -B -e "SELECT COUNT(*) FROM yiyao.prescription_diseases;" 2>/dev/null)
  if [ "$ROWS" = "1000000" ]; then
    ok "MySQL 3306，处方表 $ROWS 行"
  else
    bad "MySQL 3306 在监听，但行数为 ${ROWS:-空}（期望 1000000）"
  fi
else
  bad "MySQL 3306 未监听，看 /var/log/mysqld.log"
fi

# ------------------------------------------------------------ 3. 后端
step "3/5 后端接口（83）"
# 如果 jar 比运行中的进程新，说明刚重新编译过，必须重启才会生效
BK_PID=$(ss -lntp 2>/dev/null | grep ':83 ' | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2)
if port_up 83 && [ -n "$BK_PID" ]; then
  JAR_T=$(stat -c %Y "$JAR" 2>/dev/null || echo 0)
  PROC_T=$(stat -c %Y "/proc/$BK_PID" 2>/dev/null || echo 0)
  if [ "$JAR_T" -gt "$PROC_T" ]; then
    echo "  jar 比进程新，重启后端（旧进程 PID=$BK_PID）"
    kill "$BK_PID" 2>/dev/null
    sleep 3
  fi
fi
if port_up 83; then
  ok "已在运行（jar 与进程一致）"
else
  if [ -f "$JAR" ]; then
    cd "$APP_DIR/backend/yiyao" || exit 1
    nohup java -jar "$JAR" > /tmp/yiyao.log 2>&1 &
    echo "  已启动 PID=$!，等待端口就绪"
    printf '  '
    if wait_http "http://localhost:83/home/overview" 120; then
      ok "启动完成"
    else
      bad "启动超时，看 /tmp/yiyao.log 末尾"
    fi
  else
    bad "找不到 jar：$JAR（先 cd $APP_DIR/backend/yiyao && mvn clean package -DskipTests）"
  fi
fi
if port_up 83; then
  CODE=$(curl -s -o /dev/null -w '%{http_code}' --max-time 120 http://localhost:83/home/overview)
  if [ "$CODE" = "200" ]; then ok "/home/overview 返回 200"; else bad "/home/overview 返回 $CODE"; fi
  CODE=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 http://localhost:83/)
  if [ "$CODE" = "200" ]; then ok "前端页面 / 返回 200"; else bad "前端页面 / 返回 $CODE"; fi
fi

# ------------------------------------------------------------ 4. 大屏
step "4/5 Django 大屏（8000）"
if port_up 8000; then
  ok "已在运行"
else
  cd "$SCREEN_DIR" || exit 1
  nohup python3 manage.py runserver 0.0.0.0:8000 > /tmp/screen.log 2>&1 &
  echo "  已启动 PID=$!，等待端口就绪"
  printf '  '
  if wait_http "http://localhost:8000/api/health/" 90; then
    ok "启动完成"
  else
    bad "启动超时，看 /tmp/screen.log 末尾"
  fi
fi
if port_up 8000; then
  HEALTH=$(curl -s --max-time 30 http://localhost:8000/api/health/ 2>/dev/null)
  case "$HEALTH" in
    *'"db": true'*)     ok "大屏取数正常（db: true）" ;;
    *'"db": false'*)    bad "大屏连不上 MySQL：$HEALTH" ;;
    *)                  bad "大屏健康检查异常：${HEALTH:-无响应}" ;;
  esac
fi

# ------------------------------------------------------------ 5. 接口清单
step "5/5 13 个接口连通性（百万行聚合，逐个跑完约 1~2 分钟）"
for u in /home/overview /home/citylevel /home/age /home/top10 /home/province \
         /disease/union /disease/drug /disease/age /disease/section \
         /drug/cities /drug/hospital /drug/diseases /drug/section ; do
  # 一次请求同时拿到状态码与耗时，避免跑两遍
  out=$(curl -s -o /dev/null -w '%{http_code} %{time_total}' --max-time 180 "http://localhost:83$u")
  code=${out%% *}
  t=${out##* }
  if [ "$code" = "200" ]; then
    printf '  \033[32m[ OK ]\033[0m %-18s %6.2f 秒\n' "$u" "$t"
  else
    printf '  \033[31m[FAIL]\033[0m %-18s HTTP=%s\n' "$u" "$code"
    FAILED=1
  fi
done

# ------------------------------------------------------------ 汇总
IP=$(hostname -I | awk '{print $1}')
echo ""
if [ $FAILED -eq 0 ]; then
  printf '\033[32m全部就绪\033[0m\n'
else
  printf '\033[31m有检查项未通过，见上面 [FAIL]\033[0m\n'
fi
echo "  前端 + 接口： http://$IP:83/"
echo "  可视化大屏： http://$IP:8000/"
echo "  Kylin 控制台：http://$IP:7070/kylin   (ADMIN / KYLIN)"
echo "  YARN：       http://$IP:8088/"
echo "  HDFS：       http://$IP:50070/"
echo "  HBase：      http://$IP:16010/"
echo ""
echo "日志：后端 /tmp/yiyao.log　大屏 /tmp/screen.log　集群 /tmp/start-cluster.log"
exit $FAILED
