# Skills

Personal agent skills: a `SKILL.md` with instructions plus the scripts and templates it uses,
for any coding agent that supports skills.

| Skill | What it does |
|---|---|
| [`explainer-video`](explainer-video/) | Turns a paper or ML/math concept into a narrated, subtitled 3Blue1Brown-style ManimGL video, from storyboard to YouTube upload |
| [`exam-prep`](exam-prep/) | Turns a course folder (script, slides, recordings, past exams) into an exam-driven study kit: frequency analysis of past exams, day plan, cheatsheet, narrated theory and worked-example videos, practice sheets with answer keys, mock exam. Uses `explainer-video` for the videos |

## Install

Clone the repository and link each skill into your agent's skills folder (`<skills-dir>` below):

    git clone git@github.com:zayac/skills.git ~/Documents/skills
    ln -s ~/Documents/skills/explainer-video <skills-dir>/explainer-video
    ln -s ~/Documents/skills/exam-prep <skills-dir>/exam-prep

Edits made in the clone are live immediately; commit and push to keep them.
