create table categories (
    id serial primary key,
    name varchar(255) not null unique,
    slug varchar(255) not null unique,
    parent_id int references categories(id)
)



-- query select categoires with filter


select
    id,
    name,
    slug,
    parent_id
from categories
where parent_id is null


-- Parent 1
--     Parent 2
--         children 1
--         children 2
--     parent 3
--         parent 4
--             children 3
--             children 4

--         parent 5
--             children 5
--             children 6
--                 children 7
--                 children 8



-- we wanna search all categories related to parent 3

-- we should get
-- parent 4
-- children 3
-- children 4
-- parent 5
-- children 5
-- children 6
-- children 7
-- children 8

with recursive category_tree as (

    select 
        id,
        parent_id
    from categories
    where id = 3

    union all

    select 
        c.id,
        c.parent_id
    from categories c
    inner join category_tree ct on c.parent_id = ct.id
)


select
    id,
    name,
    slug,
    parent_id
from categories
where 
    name = 'Electronics' or id in (select id from category_tree)