USE `toys_and_models`;

SHOW FULL TABLES;

# Geoffrey - Sales

# Nombre de produits vendus par catégorie et par mois.
CREATE OR REPLACE VIEW line_ordered AS  

SELECT p.productLine, YEAR(o.orderDate) as year_of_sales, MONTH(o.orderDate) as month_of_sales, SUM(od.quantityOrdered) as sales
        FROM orderdetails as od														# Table orderdetails
		INNER JOIN orders as o ON od.orderNumber = o.orderNumber					# Table orders
		INNER JOIN products as p ON od.productCode = p.productCode					# Table products
        WHERE o.status = 'Shipped' or o.status = 'Resolved'							# Affiche seulement les produits expédiés 
		GROUP BY p.productLine, year_of_sales, month_of_sales						# Nombre de ventes par catégorie et par mois
        ORDER BY year_of_sales DESC, month_of_sales DESC, productLine ASC;			# Dans l'ordre décroissant 
        
SELECT * FROM line_ordered;

- - - - - - - - - -

# Nombre de produits vendus par échelle et par mois.

CREATE OR REPLACE VIEW scale_ordered AS

SELECT p.productScale, SUM(od.quantityOrdered) as quantity_sales, YEAR(o.orderDate), MONTH(o.orderDate)
FROM orderdetails as od
JOIN orders as o ON od.orderNumber = o.orderNumber
JOIN products as p ON od.productCode = p.productCode
WHERE (o.status = 'Shipped' or status = 'Resolved') 
GROUP BY p.productScale, YEAR(o.orderDate), MONTH(o.orderDate)
ORDER BY YEAR(o.orderDate) DESC, MONTH(o.orderDate), quantity_sales DESC;

SELECT * FROM scale_ordered;

- - - - - - - - - - 

# Nombre de produits vendus par pays ( de clients ) et par an.

CREATE OR REPLACE VIEW sales_country_customers AS

SELECT  YEAR(o.orderDate), MONTH(o.orderDate), c.country as country_customers, SUM(od.quantityOrdered) as sales_quantity
FROM orderdetails as od
JOIN orders as o ON od.orderNumber = o.orderNumber
JOIN customers as c ON c.customerNumber = o.customerNumber
WHERE (o.status = 'Shipped' or status = 'Resolved')
GROUP BY country_customers, YEAR(o.orderDate), MONTH(o.orderDate)
ORDER BY YEAR(o.orderDate) DESC, sales_quantity DESC;

SELECT * FROM sales_country_customers;

- - - - - - - - - -
/*
# Nombre de produits vendus par pays ( de bureau ) et par an.

CREATE OR REPLACE VIEW sales_country_offices AS

SELECT YEAR(o.orderDate), MONTH(o.orderDate), offi.country as country_offices, SUM(od.quantityOrdered) as sales_quantity
FROM orderdetails as od
JOIN products as p ON p.productCode = od.productCode
JOIN orders as o ON od.orderNumber = o.orderNumber
JOIN customers as c ON c.customerNumber = o.customerNumber
JOIN employees as e ON e.employeeNumber = c.salesRepEmployeeNumber
JOIN offices as offi ON e.officeCode = offi.officeCode
WHERE (o.status = 'Shipped' or status = 'Resolved')
GROUP BY offi.country, YEAR(o.orderDate), MONTH(o.orderDate)
ORDER BY YEAR(o.orderDate) DESC, offi.country ASC, sales_quantity DESC;

SELECT * FROM sales_country_offices;
*/