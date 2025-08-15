-- hämtar alla publishing_house från databasen.
-- placerar alla uppgifter för ett id på en rad.
-- export data, export to XML file, formatsetting - advanced setting: "value display format - editable".

SELECT
	p.publishing_house_id as old_id,
	p.name
FROM
	publishing_house p
