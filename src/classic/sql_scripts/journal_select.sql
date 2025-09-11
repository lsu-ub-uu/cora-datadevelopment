-- hämtar alla journal från databasen; journal, journal_title
-- placerar alla uppgifter för ett id på en rad.
-- export data, export to XML file, formatsetting - advanced setting: "value display format - editable".

SELECT
	j.journal_id AS old_id,
	jt.main_title AS title,
	jt.sub_title AS subtitle,
	j.closed_date AS end_date,
	j.eissn AS identifier_eissn,
	j.issn AS identifier_pissn,
	j.url
FROM
	journal j
	LEFT JOIN journal_title jt ON j.journal_id = jt.journal_id
