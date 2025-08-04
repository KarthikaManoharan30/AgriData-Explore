select * from agriculture_data

--SQL Queries
--1: Year-wise Trend of Rice Production Across States (Top 3)

-- step 1: find top 3 rice-producing states
with top_states as (
    select state_name
    from agriculture_data
    group by state_name 
    order by sum(rice_production) desc
    limit 3
)

-- step 2: get year-wise rice production for those top states
select
    year,
    state_name,
    sum(rice_production) as total_rice_production
from
    agriculture_data
where
    state_name in (select state_name from top_states)
group by
    year, state_name
order by
    year, total_rice_production desc
-----------------------------------------------------------------------------------------------------------------


--2: Top 5 Districts by Wheat Yield Increase Over the Last 5 Years

-- Step 1: Identify the last 5 years from the dataset
with last_five_years as 
(
select distinct year from agriculture_data order by year desc limit 5
),
-- Step 2: Get the earliest and latest year from the 5
year_range as 
(
select max(year) as latest_year,
min(year) as earliest_year 
from last_five_years 
),
-- Step 3: Get average wheat yield per district for those 2 years
district_yields as
(
select dist_name, year, avg(wheat_yield) as avg_yield
from agriculture_data 
where year in (select latest_year from year_range) 
   or year in (select earliest_year from year_range) 
group by dist_name, year
),
-- Step 4: Pivot to show yield in both years side-by-side
yield_comparison as (
select dist_name,
max(case when year = (select latest_year from year_range) then avg_yield end) as yield_now,
max(case when year = (select earliest_year from year_range) then avg_yield end) as yield_before
from district_yields
group by dist_name
)
-- Step 5: Show top 5 districts by yield increase
select
  dist_name,
  yield_before,
  yield_now,
  yield_now - yield_before as yield_increase
from yield_comparison
where yield_now is not null and yield_before is not null
order by yield_increase desc
limit 5


---------------------------------------------------------------------------------------------------------------------------




--3:  States with the Highest Growth in Oilseed Production (5-Year Growth Rate)

with recent_years as (
    select distinct year from agriculture_data order by year desc limit 5
),
oilseed_summary as (
    select state_name, year, sum(oilseeds_production) as total_production
    from agriculture_data
    where year in (select year from recent_years)
    group by state_name, year
),
pivoted as (
    select
        state_name,
        max(case when year = (select min(year) from recent_years) then total_production end) as production_start,
        max(case when year = (select max(year) from recent_years) then total_production end) as production_end
    from oilseed_summary
    group by state_name
)
select
    state_name,
    production_start,
    production_end,
    round((((production_end - production_start) / production_start) * 100)::numeric, 2) as growth_rate_percent
from pivoted
where production_start is not null and production_end is not null and production_start <> 0
order by growth_rate_percent desc
limit 5

-------------------------------------------------------------------------------------------------------------------------

--4: .District-wise Correlation Between Area and Production for Major Crops (Rice, Wheat, and Maize)

select
    dist_name,
    state_name,
    (
        (count(*) * sum(rice_production * rice_area) - sum(rice_production) * sum(rice_area)) /
        (sqrt(count(*) * sum(rice_production * rice_production) - power(sum(rice_production), 2)) *
         sqrt(count(*) * sum(rice_area * rice_area) - power(sum(rice_area), 2)))
    ) as rice_corr
from agriculture_data
where rice_production is not null and rice_area is not null
group by dist_name, state_name
having
    sqrt(count(*) * sum(rice_production * rice_production) - power(sum(rice_production), 2)) <> 0 and
    sqrt(count(*) * sum(rice_area * rice_area) - power(sum(rice_area), 2)) <> 0


--------------------------------------------------------------------------------------------------------------------------------	
--5.Yearly Production Growth of Cotton in Top 5 Cotton Producing States


with total_cotton as (
    select state_name, sum(cotton_production) as total
    from agriculture_data
    group by state_name
    order by total desc
    limit 5
),
cotton_trend as (
    select year, state_name, sum(cotton_production) as yearly_production
    from agriculture_data
    where state_name in (select state_name from total_cotton)
    group by year, state_name
)
select * from cotton_trend
order by year, state_name

------------------------------------------------------------------------------------------------


--6: Districts with the Highest Groundnut Production in 2017


SELECT dist_name, state_name, groundnut_production
FROM agriculture_data
WHERE year = 2017
ORDER BY groundnut_production DESC
LIMIT 7;

--------------------------------------------------------------------------------------------------------
--7: Annual Average Maize Yield Across All States

select year, round(avg(maize_yield)::numeric, 2) as avg_maize_yield
from agriculture_data
group by year
order by year

-------------------------------------------------------------------------------------------------------------


--8: Total Area Cultivated for Oilseeds in Each State

select state_name, round(sum(oilseeds_area)::numeric,2) as total_oilseeds_area
from agriculture_data
group by state_name
order by total_oilseeds_area desc

----------------------------------------------------------------------------------------------
--9: Districts with the Highest Rice Yield

select dist_name, state_name, max(rice_yield) as max_rice_yield
from agriculture_data
group by dist_name, state_name
order by max_rice_yield desc
limit 5

-------------------------------------------------------------------------------------------------

--10: Compare the Production of Wheat and Rice for the Top 5 States Over 10 Years

with top_states as (
    select state_name, sum(wheat_production + rice_production) as total_production
    from agriculture_data
    group by state_name
    order by total_production desc
    limit 5
)
select
    year,
    state_name,
    round(sum(wheat_production)::numeric, 2) as total_wheat,
    round(sum(rice_production)::numeric, 2) as total_rice
from agriculture_data
where state_name in (select state_name from top_states)
group by year, state_name
order by year, state_name

-----------------------------------------------------------------------------------------------------------------

