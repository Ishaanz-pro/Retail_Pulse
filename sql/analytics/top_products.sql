SELECT product_id, name, category, SUM(revenue) AS revenue,
       RANK() OVER (ORDER BY SUM(revenue) DESC) AS revenue_rank
FROM sales_fact
GROUP BY product_id, name, category
ORDER BY revenue_rank;
