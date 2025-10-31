import re
import html


def clean_rich_text(input: str) -> str:
    output = html.unescape(input)

    output = _remove_empty_elements(output)
    output = _format_blocks(output)
    output = _format_ul(output)
    output = _format_ol(output)
    output = _strip_html_tags(output)

    # Unescape double encoded tags such as &amp;amp
    return html.unescape(output).strip()


def _remove_empty_elements(input: str) -> str:
    return re.sub(r"<(p|ul|ol|li)>\s*</\1>", "", input)


def _format_blocks(input: str) -> str:
    block_tags = [
        "p",
        "ol",
        "ul",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "pre",
    ]

    output = input
    for tag in block_tags:
        output = output.replace(f"</{tag}>", f"</{tag}>\n\n")
    return output


def _format_ul(input: str) -> str:
    def replace_ul_block(match):
        ul_content = match.group(1)
        li_items = re.findall(r"<li>(.+?)</li>", ul_content, flags=re.DOTALL)
        return "\n".join(f"• {item}" for item in li_items)

    return re.sub(r"<ul>(.+?)</ul>", replace_ul_block, input, flags=re.DOTALL)


def _format_ol(input: str) -> str:
    def replace_ol_block(match):
        ol_content = match.group(1)
        li_items = re.findall(r"<li>(.+?)</li>", ol_content)
        return "\n".join(f"{i+1}. {item}" for i, item in enumerate(li_items))

    return re.sub(r"<ol>(.+?)</ol>", replace_ol_block, input, flags=re.DOTALL)


def _strip_html_tags(input: str) -> str:
    html_tags_to_remove = [
        "p",
        "em",
        "strong",
        "sub",
        "sup",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "pre",
        "br",
        "div",
        "span",
        "b",
        "i",
        "u",
        "strike",
        "del",
        "ins",
        "small",
        "big",
        "code",
        "kbd",
        "samp",
        "var",
        "cite",
        "abbr",
        "acronym",
    ]

    for tag in html_tags_to_remove:
        input = re.sub(f"<{tag}(?:\\s[^>]*)?>", "", input, flags=re.IGNORECASE)
        input = re.sub(f"</{tag}>", "", input, flags=re.IGNORECASE)

    return input


if __name__ == "__main__":
    sample_input = "&lt;p&gt;This symposium explores undergraduates’ identity and learning processes in contemporary higher education. In particular, it asks: How do different learning/teaching contexts and discourses about gender, class, sexuality, age etc. inform undergraduates’ choices, educational and social strategies and their experiences of university?&lt;/p&gt;&lt;p&gt;Drawing on a cross-national comparative interview study, Nyström, Salminen Karlsson and Jackson’s paper explores constructions and understandings of men’s effort, talent, academic failure and success within different elite contexts. Masculinity and affect are also central themes in Ottemo’s paper, which draws on an ethnographic study that examined, from a queer-perspective, passionate reasons for being interested in education and learning in technology. The final paper, by Bøe, Ryder &amp;amp; Ulriksen, explores STEM choices and especially women's choices, based on findings from a large, mixed-methods European study called IRIS.&lt;/p&gt;&lt;p&gt;Hence, the symposium discusses processes that lie beneath the gendered and classed patterns of students’ trajectories and outcomes in higher education. Such discussions are vital because in the Nordic countries, as in Europe overall, women have constituted the majority of undergraduate students since the 1990s and, in general, are more likely than men to perform well and complete their studies. Nevertheless, STEM subjects (science, technology, engineering and mathematics), just as academia overall, are still male-dominated in many respects. Our papers and discussion will reflect six national perspectives, from Norway, Sweden, UK, Denmark, Italy, and Slovenia.&lt;/p&gt;&lt;p&gt;Papers:&lt;/p&gt;&lt;ol&gt;&lt;li&gt;&lt;strong&gt;1.      &lt;/strong&gt;&lt;strong&gt;Reflections of and about men’s failure – Gender and academic achievement in three educational elite contexts  &lt;/strong&gt;&lt;/li&gt;&lt;/ol&gt;&lt;p&gt;Anne-Sofie Nyström, Uppsala University, anne-sofie.nystrom@gender.uu.se; Carolyn Jackson, Lancaster University, c.jackson2@lancaster.ac.uk; Minna Salminen Karlsson, Uppsala University, minna.salminen@gender.uu.se.&lt;/p&gt;&lt;ol&gt;&lt;li&gt;&lt;strong&gt;2.      &lt;/strong&gt;&lt;strong&gt;Between instrumentality and passion: The gendering of student subjectivities at two engineering programs at a Swedish university of technology&lt;/strong&gt;&lt;strong&gt;&lt;/strong&gt;&lt;/li&gt;&lt;/ol&gt;&lt;p&gt;Andreas Ottemo, University of Gothenburg, andreas.ottemo@ped.gu.se&lt;/p&gt;&lt;ol&gt;&lt;li&gt;&lt;strong&gt;3.      &lt;/strong&gt;&lt;strong&gt;The process of choosing STEM higher education: Messages from the IRIS project&lt;/strong&gt;&lt;/li&gt;&lt;/ol&gt;&lt;p&gt;Maria Vetleseter Bøe, University of Oslo, m.v.boe@naturfagsenteret.no; Jim Ryder, University of Leeds, j.ryder@education.leeds.ac.uk; Lars Ulriksen, University of Copenhagen, ulriksen@ind.ku.dk&lt;/p&gt;&lt;p&gt; &lt;/p&gt;&lt;p&gt;Discussant: Elisabet Öhrn, University of Gothenburg, elisabet.ohrn@ped.gu.se&lt;/p&gt;&lt;p&gt; &lt;/p&gt;&lt;p&gt;&lt;strong&gt;Reflections of and about men and failure – Gender and academic achievement in three educational elite contexts  &lt;/strong&gt;&lt;/p&gt;&lt;p&gt;Anne-Sofie Nyström, Carolyn Jackson &amp;amp; Minna Salminen Karlsson&lt;/p&gt;&lt;p&gt;This paper explores constructions and understandings of the ways in which effort, talent, academic success and failure are gendered in elite, higher education contexts, with a particular focus on these constructions in relation to men and masculinities.  It draws on data from a large, ongoing, three-year (2015-2018), cross-national (Sweden and England) comparative interview project that investigates how constructions of masculinities and student identities inform strategies for coping with risks of academic failure and/or striving for success. The project focuses on three elite undergraduate programmes: Medicine, Law and Engineering. Data are being generated by observations, focus group interviews and individual interviews with students, student representatives, study advisers, lecturers and directors of studies. The project addresses the following research questions:&lt;/p&gt;&lt;ol&gt;&lt;li&gt;How are ‘successful’ and ‘unsuccessful’ student identities perceived and constructed among male undergraduates in different, but highly competitive, educational contexts?&lt;/li&gt;&lt;li&gt;What are the main practices and self-worth protection strategies male students use to accomplish successful identities or avoid unsuccessful ones?&lt;/li&gt;&lt;li&gt;How does masculinity and its intersections with social class, ethnicity and age, inform staff and students’ understandings of the reasons for academic failure and success?&lt;/li&gt;&lt;li&gt;Are there differences between a) Swedish and English HE contexts and b) programmes that hinder or facilitate certain identities or strategies?&lt;/li&gt;&lt;li&gt;How do the strategies and practices (in 2) relate to persistence, achievement and wellbeing?&lt;/li&gt;&lt;/ol&gt;&lt;p&gt;This first paper from the project focuses on data from academic and administrative staff in one Swedish university, as well as representatives for student organizations.  It explores, in particular, how success and failure are constructed and perceived within the different programmes. These constructions vary between the programmes, partly because of the ways in which the programme content and the grades are related to the future labour market in the different professions. We discuss the ways that success and failure are made more or less important in students’ lives, both by staff and by students themselves, and the ways in which these concepts are rendered visible at particular points, and how such instances relate to the programmes’ different structures and cultures. By examining such issues with a gender perspective we will begin to shed light on some of the ways in which male undergraduates’ learner identities are constructed and negotiated within these privileged academic contexts.&lt;/p&gt;&lt;p&gt; &lt;/p&gt;&lt;p&gt;&lt;strong&gt;Between instrumentality and passion: The gendering of student subjectivities at two engineering programs at a Swedish university of technology&lt;/strong&gt;&lt;/p&gt;&lt;p&gt;Andreas Ottemo&lt;/p&gt;&lt;p&gt;In this paper, I explore student subjectivities articulated in two programs at a Swedish university of technology: Computer Science and Engineering (CSE) and Chemical Engineering (CE). The paper builds on the assumption that the articulation of gendered subjectivities in these programs relates to how technology is articulated. Much previous research on gender and technology has tended to primarily focus on the “failure” of linking women/femininity to technology. In this paper I, instead, take on a perspective inspired by queer theory in the sense that I focus on norms that articulate masculinity with technology. Theoretically and methodologically, I adopt a post-structural perspective primarily based on discourse theory, as developed by Laclau and Mouffe (1985). I also draw on feminist technoscience research and on Butler’s (1988, 1990, 1993) notion of gender, performativity, and the heterosexual matrix. Empirically, the discussion is based on a recently concluded ethnographic study within a Swedish university of technology.&lt;/p&gt;&lt;p&gt;Drawing on a critique that has suggested that gender and technology research often fails to address such aspects, I will call attention to the role of passion, desire and (hetero)sexuality in the production of connections between masculinity and technology (cf. Henwood &amp;amp; Miller 2001, Landström 2006, Mellström 2004, Stepulevage 2001). Somewhat in contrast to this theme, I will also discuss more instrumental approaches to higher technology education. In the analysis, I suggest that the formal education students receive fails, for various reasons, to subjectively engage many students. Consequently, many students adopt an instrumental approach to their education, emphasizing the future exchange value of their formal degree, rather than subjective meaningfulness or the significance of the subject matter as such. I also argue that in failing to “recruit” students, formal education can be considered as privileging the already-passionate student, whose interest in technology is not so easily derailed, even when encountering education that fails to engage subjectively. This “passionate student” subject position is articulated primarily in the CSE program, mainly in informal, student cultural contexts. Here, I argue that technology, corporeality, desire, and embodied computer interest, are configured in a manner that derives intelligibility from the heterosexual matrix and contributes to the CSE program’s hetero-masculine connotations. On the other hand, the absence of the “passionate student” subject position in the CE program, appears to contribute to this program’s relative gender inclusiveness.&lt;/p&gt;&lt;p&gt; &lt;/p&gt;&lt;p&gt;&lt;strong&gt;The process of choosing STEM higher education: Messages from the IRIS project&lt;/strong&gt;&lt;/p&gt;&lt;p&gt;Maria Vetleseter Bøe, Jim Ryder &amp;amp; Lars Ulriksen&lt;/p&gt;&lt;p&gt;This paper reports on the European research project IRIS (Interest and Recruitment in Science)(2010-2013). In IRIS, six partners from five participating countries worked together to improve our understanding of students’ participation and choice in science and technology education, with particular emphasis on gender. The IRIS research activities comprised studies with quantitative, qualitative or mixed-method approaches, targeting both secondary and tertiary level respondents and informants. Some of the studies only used data from within one of the participating countries whereas others worked comparatively with data from different countries. In this paper, we present some insights from the project, paying particular attention to gender.&lt;/p&gt;&lt;p&gt;As a first message from IRIS we argue that educational choice should be seen as a process that takes place over time – before, at, and after specific decision points. A striking feature of the choice process is that young people’s accounts of their choices are in constant change. For example, stories about their interests and aspirations in the past tend to be adjusted to fit their present perspective on their choice. In a longitudinal Danish study, for example, a young woman originally stated that she did not want to follow a course leading to teaching. In a later interview, however, after deciding to enrol in such a course after all, she stated that she had always wanted to become a teacher.&lt;/p&gt;&lt;p&gt;The second message relates to the importance of identity in choice processes, which was a starting point for the IRIS project. Studies in IRIS demonstrate how young people negotiate their identities within social structures, and how this affects recruitment and retention in STEM higher education. For example, a dominant discourse in STEM is that “science is difficult and for the clever”. Therefore, young people need to see themselves as ‘clever’ in order to pursue a STEM pathway. Given that young women are more likely than men to doubt their abilities and ‘cleverness’ in science and mathematics, this discourse may be particularly alienating to many women, but also to some men. To make it easier for more young people to negotiate their identities within STEM, it appears fruitful to broaden the range of discourses that are available.&lt;/p&gt;&lt;p&gt;A third message in many ways builds on the issue of available discourses. One of the studies in IRIS demonstrated that the “science as difficult and for the clever” discourse can be challenged in a way that makes it less harmful for STEM participation. After participating in a recruitment event at the Norwegian University for Science and Technology, secondary girls believed a STEM study would be even more difficult and demanding than they thought before they came. However, this did not lead to less confidence in their ability to succeed in a STEM study. The reason appears to be that the girls met current STEM students who served as ‘available role models’, stressing that “it is tough for everybody” and “normal people can do it”.&lt;/p&gt;"
    print(clean_rich_text(sample_input))
