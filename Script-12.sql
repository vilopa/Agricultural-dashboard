SELECT AreaID, SUM(Value) AS Total_Sales
FROM Agricultural_Production_Data
GROUP BY AreaID
ORDER BY Total_Sales DESC;


SELECT Year_ID, AVG(Value) AS Average_Value
FROM Agricultural_Production_Data
GROUP BY Year_ID
ORDER BY Year_ID;



SELECT AreaID, Item_Code_CPC, SUM(Value) AS Total_Sales
FROM Agricultural_Production_Data
WHERE Year_ID = 2023
GROUP BY AreaID, Item_Code_CPC
ORDER BY Total_Sales DESC;




SELECT a.AreaID, a.Year_ID, SUM(a.Value) AS Total_Value, b.Region, c.Year
FROM Agricultural_Production_Data a
INNER JOIN Area b ON a.AreaID = b.AreaID
LEFT JOIN Year c ON a.Year_ID = c.Year_ID
WHERE a.Year_ID BETWEEN 2020 AND 2025
AND c.Year > '2020-01-01'
GROUP BY a.AreaID, a.Year_ID
ORDER BY Total_Value DESC;


SELECT a.AreaID, a.Year_ID, AVG(a.Value) AS Average_Value, b.Region
FROM Agricultural_Production_Data a
INNER JOIN Area b ON a.AreaID = b.AreaID
LEFT JOIN Year c ON a.Year_ID = c.Year_ID
WHERE a.Year_ID BETWEEN 2020 AND 2025
GROUP BY a.AreaID, a.Year_ID
ORDER BY Average_Value DESC;









