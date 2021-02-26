SELECT column_N__c1_c2
FROM table_N__t1_t2
WHERE op_N__aggregate__c1_c2__column_N__c1_c2

N = 1,2,3,...,any
op = >,<,=,>=,=<,!=,between,in,not in


SELECT column_EN__c1_c2
FROM table_EN__t1_t2
WHERE op_EN_column_EN__c1_c2

E -> exactly


SELECT aggregate__c1_c2__column_N__c1_c2
FROM join_inner_table_N__t1_t2__on_column_N__c1_c2
GROUP BY column_N__c1_c2
HAVING op_N__aggregate__c1_c2__column_N__c1_c2
ORDER BY column_N__c1_c2


N = 1,2,3,...,any
aggregate = COUNT, MIN, MAX, SUM, AVG