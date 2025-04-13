query_generation_prompt = """
### Instructions ###

Your task is to convert a question into a SQL SELECT statement, given the following database sudo-schema from Couchbase.

Adhere to these rules:

-- Deliberately go through the question and database schema word by word to appropriately answer the question.
-- When referring to a table, follow the `bucket_name`.`scope_name`.`collection_name` structure which is the Couchbase format. 
-- Carefully observe the nested attributes mentioned since Couchbase is a NoSQL database that allows de-normalized data.
-- When creating a ratio, always cast the numerator as float.
-- Do not use the COALESCE function.
-- Do not explain your answer.



### Input ###

This SQL SELECT statement will run on the Couchbase database whose schema is represented by the following schema:
{concat_schemas}

Here is the question:
{question}



### When joining tables use this format ###

SELECT
    users.user_id AS users_id, users.name AS users_name, users.email AS users_email, users.roles AS users_roles, users.department AS users_department,
    products.product_id AS products_id, products.user_id AS products_user_id, products.name AS products_name, products.cost AS products_cost, products.quantity AS products_quantity, products.date_created AS products_date_created, products.date_updated AS products_date_updated,
    homes.home_id AS homes_id, homes.type AS homes_type, homes.user_id AS homes_user_id, homes.address_1 AS homes_address_1, homes.city AS homes_city, homes.state AS homes_state, homes.zip_code AS homes_zip_code, homes.country AS homes_country, homes.date_created AS homes_date_created, homes.date_updated AS homes_date_updated
FROM
    users
JOIN
    products ON users.user_id = products.user_id
JOIN
    homes ON users.user_id = homes.user_id



### Formatting the query correctly ###

- for the SELECT syntax, instead of "Select `travel-sample`.`inventory`.`hotel`.id", use "Select id" directly 
- for the WHERE predicates, instead of "Where `travel-sample`.`inventory`.`hotel`.pets_ok = TRUE", use "Where pets_ok = TRUE" directly

%s
"""