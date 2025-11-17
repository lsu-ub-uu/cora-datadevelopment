-- hämtar alla subject baserat på domän från databasen; subject, subject_name
-- placerar alla uppgifter för ett id på en rad.
-- export data, export to XML file, formatsetting - advanced setting: "value display format - editable".

SELECT
	s.domain,
	s.subject_id as old_id,
	s.closed_date as end_date,
	sn_swe.subject_name as name_swe,
	sn_eng.subject_name as name_eng,
	sp.subject_id as broader_id,
	sp.parent_subject_id, --används inte, enbart för att hämta och läsa data rätt till broader_id
	string_agg(pre.subject_id:: text, ',') as earlier_id
FROM
    subject s
    left join subject_name sn_swe on s.subject_id = sn_swe.subject_id and sn_swe.locale = 'sv' -- lägger på en rad
    left join subject_name sn_eng on s.subject_id = sn_eng.subject_id and sn_eng.locale = 'en' -- lägger på en rad
    left join subject_parent sp on s.subject_id = sp.parent_subject_id
    left join subject_predecessor pre on s.subject_id = pre.predecessor_subject_id
WHERE
    s.subject_type_id = '54' and s.domain = %(domain)s
GROUP BY
    s.domain, s.subject_type_id, s.closed_date, sn_swe.subject_name, sn_eng.subject_name, s.subject_id, sp.subject_id, sp.parent_subject_id;