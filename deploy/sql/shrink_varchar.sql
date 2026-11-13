-- ============================================================
-- yiyao 维表列宽收窄
--
-- 背景：
--   5 张维表的文本列全部是 varchar(1000)，而实测最长只有 2~64 字符。
--   100 万行事实表按药品名分组时，每行都拖着 1000 字节进临时表，
--   只是搬空字节就把查询拖到了 9~12 秒。
--
-- 做法：
--   遍历 information_schema 里 CHARACTER_MAXIMUM_LENGTH > 255 的 varchar 列，
--   逐列取 MAX(CHAR_LENGTH()) 后 ALTER 成 VARCHAR(GREATEST(最小宽度, 最大长度 × 2))。
--   宽度由脚本自己量，不靠人猜，避免截断。
--
-- 执行：
--   mysql -uroot -p123456 yiyao < shrink_varchar.sql
--
-- 说明：
--   只改 MySQL 里的表结构，不影响 Hive / Kylin 侧的数据——那边是 HDFS 上的
--   文本文件，与 MySQL 列宽无关，Cube 仍是 READY 状态。
--   改完不需要重启后端，立即生效。
--
-- 实测结果：t_view_drug 数据部分 61.6 MB。
-- ============================================================

DELIMITER $$

DROP PROCEDURE IF EXISTS shrink_varchar $$

CREATE PROCEDURE shrink_varchar(IN p_table VARCHAR(64), IN p_min INT)
BEGIN
  DECLARE done INT DEFAULT 0;
  DECLARE c    VARCHAR(64);
  DECLARE mx   INT;
  DECLARE cur CURSOR FOR
    SELECT COLUMN_NAME FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = 'yiyao' AND TABLE_NAME = p_table
      AND DATA_TYPE = 'varchar' AND CHARACTER_MAXIMUM_LENGTH > 255;
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

  OPEN cur;
  read_loop: LOOP
    FETCH cur INTO c;
    IF done = 1 THEN LEAVE read_loop; END IF;

    SET @q = CONCAT('SELECT MAX(CHAR_LENGTH(`', c, '`)) INTO @mx FROM `', p_table, '`');
    PREPARE s FROM @q; EXECUTE s; DEALLOCATE PREPARE s;

    SET mx = IFNULL(@mx, 0);
    IF mx > 0 THEN
      SET @a = CONCAT('ALTER TABLE `', p_table, '` MODIFY `', c,
                      '` VARCHAR(', GREATEST(p_min, mx * 2), ')');
      PREPARE s2 FROM @a; EXECUTE s2; DEALLOCATE PREPARE s2;
    END IF;
  END LOOP;
  CLOSE cur;
END $$

DELIMITER ;

CALL shrink_varchar('t_view_drug',    32);
CALL shrink_varchar('t_view_disease', 32);
CALL shrink_varchar('t_view_section', 32);
CALL shrink_varchar('t_view_hosp',    32);
CALL shrink_varchar('t_view_areas',   32);

DROP PROCEDURE IF EXISTS shrink_varchar;

-- 校验：各表数据与索引占用
SELECT TABLE_NAME,
       ROUND(DATA_LENGTH  / 1024 / 1024, 1) AS data_MB,
       ROUND(INDEX_LENGTH / 1024 / 1024, 1) AS idx_MB
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'yiyao'
ORDER BY DATA_LENGTH DESC;
