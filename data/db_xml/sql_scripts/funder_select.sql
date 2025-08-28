-- hämtar alla funder från databasen; funder, funder_name
-- placerar alla uppgifter för ett id på en rad.
-- export data, export to XML file, formatsetting - advanced setting: "value display format - editable".

SELECT
	f.funder_id as old_id,
	f.funder_name as name_swe,
	fn.funder_name as name_eng,
	f.closed_date as end_date,
	f.orgnumber as "identifier_organisationNumber",
	f.doi as identifier_doi,
	f.funder_name_locale as locale_swe,
	fn.locale as locale_eng,
	fn.funder_name_id
FROM
	funder f
	left join funder_name fn on f.funder_id = fn.funder_id
