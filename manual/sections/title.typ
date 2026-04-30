#import "../constants.typ": color, spacing

#let signField() = {
    set text(size: 8pt, fill: gray)
    grid(
        columns: (1fr, auto, 60%),
        column-gutter: 2pt,

        [#v(1em)#line(length: 100%, stroke: 0.3pt)],
        text(size: 12pt)[/],
        [#v(1em)#line(length: 100%, stroke: 0.3pt)],

        [(подпись)], [], [(Ф.И.О.)],
    )
}

#set align(center)
#set par(spacing: 0.5em, first-line-indent: 0cm, justify: false)

Государственное бюджетное профессиональное образовательное учреждение

*«Академия Инженерных Технологий и Управления»*
#line(length: 100%, stroke: 0.3pt)

#block(above: spacing.xl)[
    #text(size: 18pt)[*МЕТОДИЧЕСКОЕ ПОСОБИЕ*]

    по выполнению практического задания
]

#block(above: spacing.lg, width: 60%)[
    #set text(weight: "bold")
    Модуль 1.

    Участие в проектировании архитектуры интеллектуальных интегрированных систем
]

#block(above: spacing.lg, width: 60%)[
    Специальность: 09.02.08

    Интеллектуальные интегрированные системы

    Форма обучения: очная
]

#block(above: spacing.xxl)[
    #set align(left);
    #columns(2)[
        *Составлено:*

        Преподаватель ПМ.03
        #signField()

        #colbreak()

        *Утверждено:*

        Председатель ПЦК специальности
        #signField()
    ]
]

#v(1fr)

2026
