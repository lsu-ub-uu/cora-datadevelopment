-- hämtar alla series baserat på domän från databasen; series, series_title, series_alternative_title, series_relation, publication_type
-- placerar alla uppgifter för ett id på en rad.
-- export data, export to XML file, formatsetting - advanced setting: "value display format - editable".

  
SELECT
	s.domain,
	s.series_id as old_id,
	st.main_title as title,
	st.sub_title as subtitle,
	sat.main_title as alternative_title,
	sat.sub_title as alterantive_subtitle,
	s.closed_date as end_date,
	s.issn as identifier_pissn,
	s.eissn as identifier_eissn,
	s.format_id,
	f.format_code,
	s.url,
	s.notes as external_note,
	s.publication_type_id,
	pt.publication_type_code,
	srp.relation_type_id,
	srp.relative_id as relative_id_host,
	srp.series_id,
	sre.relation_type_id,
	string_agg(sre.relative_id:: text, ',') as relative_id_preceding,
	sre.series_id,
	s.organisation_id
FROM
	series s
	left join series_title st on s.series_id = st.series_id
	left join series_alternative_title sat on s.series_id = sat.series_id
	left join format f on s.format_id = f.format_id
	left join series_relation srp on s.series_id = srp.series_id and srp.relation_type_id = '52'
	left join series_relation sre on s.series_id = sre.series_id and sre.relation_type_id = '50'
	left join publication_type pt on s.publication_type_id = pt.publication_type_id --borde_vara_string_agg?
WHERE
	s.domain = 'varldskulturmuseerna'
GROUP BY
	s.domain, s.series_id, st.main_title, st.sub_title, sat.main_title, sat.sub_title, s.closed_date, 
	s.issn, s.eissn, s.format_id, f.format_code, s.url, s.notes, s.publication_type_id, 
	pt.publication_type_code, srp.relation_type_id, srp.relative_id, srp.series_id, sre.relation_type_id, 
	sre.series_id, s.organisation_id;
	
  
	
	
	
	
	
	
	