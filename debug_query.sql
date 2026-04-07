SELECT COUNT(*) as count, departemen_id, level FROM core_asetdepartemen GROUP BY departemen_id, level ORDER BY departemen_id, level;

SELECT u.username, u.departemen_id, d.nama_departemen FROM core_customuser u LEFT JOIN core_departemen d ON u.departemen_id = d.id WHERE u.username IN ('fasta', 'anisia');

SELECT id, nama_departemen FROM core_departemen;

SELECT id, nama, level, departemen_id, parent_id FROM core_asetdepartemen WHERE departemen_id IN (SELECT id FROM core_departemen WHERE nama_departemen = 'Operasional') ORDER BY level, id;
