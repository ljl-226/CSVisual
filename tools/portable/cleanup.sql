-- ---------------------------------------------------------------------------
-- 便携版初始化脚本的最后一段：清掉自动化测试留下的脏数据
--
-- 开发过程中为了验证「上传头像 / 恢复默认 / 申请临时密码」这类功能，
-- 注册过一批 tav 开头的账号。它们对评委没有任何价值，留在 818 个演示用户里
-- 反而会让人以为系统被人乱注册过，所以出厂前统一清掉。
--
-- 注意两条 MySQL 的规矩：
--   1. DELETE ... WHERE id IN (SELECT ... FROM 同一张表) 会撞 1093 错误，
--      删 user 表本身时必须再套一层派生表；
--   2. 先删子表再删 user，顺序不能反。
-- ---------------------------------------------------------------------------

DELETE FROM `algorithm_solution_like` WHERE user_id IN (SELECT id FROM `user` WHERE username LIKE 'tav%');
DELETE FROM `algorithm_submit`       WHERE user_id IN (SELECT id FROM `user` WHERE username LIKE 'tav%');
DELETE FROM `algorithm_solution`     WHERE user_id IN (SELECT id FROM `user` WHERE username LIKE 'tav%');
DELETE FROM `answer_record`          WHERE user_id IN (SELECT id FROM `user` WHERE username LIKE 'tav%');
DELETE FROM `wrong_question`         WHERE user_id IN (SELECT id FROM `user` WHERE username LIKE 'tav%');
DELETE FROM `favorite`               WHERE user_id IN (SELECT id FROM `user` WHERE username LIKE 'tav%');
DELETE FROM `study_record`           WHERE user_id IN (SELECT id FROM `user` WHERE username LIKE 'tav%');
DELETE FROM `feedback`               WHERE user_id IN (SELECT id FROM `user` WHERE username LIKE 'tav%');
DELETE FROM `memory_vector`          WHERE note_id IN (SELECT id FROM `memory_note` WHERE user_id IN (SELECT id FROM `user` WHERE username LIKE 'tav%'));
DELETE FROM `memory_note`            WHERE user_id IN (SELECT id FROM `user` WHERE username LIKE 'tav%');
DELETE FROM `chat_record`            WHERE user_id IN (SELECT id FROM `user` WHERE username LIKE 'tav%');
DELETE FROM `chat_session`           WHERE user_id IN (SELECT id FROM `user` WHERE username LIKE 'tav%');
DELETE FROM `password_request`       WHERE user_id IN (SELECT id FROM `user` WHERE username LIKE 'tav%');

-- 派生表写法：MySQL 不允许一边删 user 一边在同一条语句里 SELECT user
DELETE FROM `user` WHERE id IN (SELECT id FROM (SELECT id FROM `user` WHERE username LIKE 'tav%') AS t);

-- 临时密码工单是功能验证时产生的（student 的测试单），出厂不预置，
-- 评委想看流程自己在页面上申请一遍更直观
DELETE FROM `password_request`;
